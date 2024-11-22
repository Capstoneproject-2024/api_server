from gensim.models import fasttext
import numpy as np
from FileReader import *
from enum import IntEnum
from datetime import datetime

class Matcher:
    def __init__(self, modelpath='models/cc.ko.300.bin.gz', use_model=True):
        self.books = []
        self.reviews = []
        if use_model:
            self.model = fasttext.load_facebook_vectors(modelpath)
        self.reader = Filereader()
        self.review_proportion = 0.5    # Proportion of Review
        self.time_format = "%y%m%d-%H%M%S"

        self.keywords = {}              # { book_title: {info: [], review: []}} Caching the keywords for testing
        self.keywords_categorized = {}  # { Keyword_category: [book1, book2, ...], Keyword_category: [...] }

        self.set_keywords()
        print("SimMatcher.py: sim_matcher ready")

    def print_all_keywords(self):
        print("------------------------------------------------------------")
        for title, keywords in self.keywords.items():
            print(f'Title: "{title}"\n'
                  f'Info Keywords  : {keywords[Keytype.INFO.name]}\n'
                  f'Review Keywords: {keywords[Keytype.REVIEW.name]}\n')
        print("------------------------------------------------------------")

    def print_all_keywords_json(self):
        """
        Save current info keyword and review keyword in json format
        :return: None
        """
        current_time = datetime.now().strftime(self.time_format)
        file_name = "results/keywords_" + current_time + ".json"
        with open(file_name, mode="w", encoding="utf-8") as file:
            json.dump(self.keywords, file, ensure_ascii=False, indent=4)

    def set_keywords(self,
                     book_keyword_path='BookInfo.txt',
                     review_keyword_path='data/keywords/review_keyword_basic.csv'):
        """
        Load keywords from review and book information files.
        Only for testing level. It should be replaced with DB API.
        :param book_keyword_path:
        :param review_keyword_path:
        :return:
        """
        # TODO
        """
        WARNING: If we try to get data from API, we should get both review and books
                from API. API use book_id as a title.
        """
        #self.getBooks(book_path=book_keyword_path)
        # Change for select review file { Json / CSV }
        # self.getReviews_json(review_path=review_keyword_path)
        # self.getReviews_csv(review_path=review_keyword_path)
        self.getReviews_API()
        self.getBooks_API()

        for book in self.books:
            self._add_keyword(book[0], book[1], Keytype.INFO)       # [0] = title, [1] = info

        for review in self.reviews:
            self._add_keyword(review[0], review[1], Keytype.REVIEW)  # [0] = title, [1] = review keywords

        print("SimilarityMatcher.py: Keywords set")

    def _add_keyword(self, title: str, keywords: list, key_type: int):
        # TODO 현재 한 책에 대한 복수개의 리뷰 처리가 안되어있음 -> 처리 완
        if title not in self.keywords:
            self.keywords[title] = {Keytype.INFO.name: [], Keytype.REVIEW.name: []}

        if key_type == Keytype.REVIEW and keywords not in self.keywords[title][Keytype.REVIEW.name]:
            self.keywords[title][Keytype.REVIEW.name].append(keywords)

        elif key_type == Keytype.INFO:
            self.keywords[title][Keytype.INFO.name] = keywords

    def _s2v_mean(self, sentence: str, voo='similar'):
        """
        Calculate vector of a single sentence using arithmetic mean
        :param sentence:
        :return:
        """
        words = sentence.split()
        word_vec = []

        for word in words:
            if word in self.model:
                word_vec.append(self.model[word])
            else:
                if voo == 'similar':
                    # if word doesn't exist in model, find the most similar word in model
                    similar_word = self.model.most_similar(word, topn=1)[0][0]
                    word_vec.append(self.model[similar_word])
                    print(f'{word} not in model -> changed into {similar_word}')
        return np.mean(word_vec, axis=0)

    def _s2v_single(self, word: str):
        """
        Get sentence vector from Word2Vec model
        :param word: sentence or word to calculate vector
        :return: vector of sentence
        """
        if word in self.model:
            return self.model[word]
        else:
            sim_word = self.model.most_similar(word, topn=1)[0][0]
            return self.model[sim_word]

    def _cosine_similarity(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        return dot_product/(norm_a * norm_b)

    def sentence_similarity(self, sen1: str, sen2: str):
        vec1 = self._s2v_mean(sen1)
        vec2 = self._s2v_mean(sen2)
        return self._cosine_similarity(vec1, vec2)

    def _test_similarity(self, word1: str, word2: str):
        word1_vec = self._s2v_single(word1)
        word2_vec = self._s2v_single(word2)
        print(f"Word1: '{word1}', Word2: '{word2}', similarity: '{self._cosine_similarity(word1_vec, word2_vec)}'")

    def getBooks(self, book_path='BookInfo.txt'):
        """
        Read book information from publishers
        [ ['title', ['key', 'words', .....] ]...... ]
        :param book_path:
        :return:
        """
        self.books = self.reader.readBooks(book_path)



    def getReviews_json(self, review_path='data.json'):
        """
        Read reviews from json file
        [ ['title', ['key', 'words', .....] ]...... ]
        :param review_path:
        :return:
        """
        self.reviews = self.reader.readReviewFromJson(review_path)

    def getReviews_csv(self, review_path='results/POS_before_extraction_stopwords.csv'):
        self.reviews = self.reader.readReviewFromCSV(review_path)

    def getReviews_API(self):
        self.reviews = self.reader.readReviewFromAPI()

    def getBooks_API(self):
        self.books = self.reader.readInfoFromAPI()

    def set_proportion(self, review_proportion: int):
        if 0 <= review_proportion <= 100:
            self.review_proportion = review_proportion/100
        else:
            print("WARNING: Proportion should be in 0~100")

    def match_both(self, title_in: str, keywords_in: list, recommend_number=5):
        """
        :param title_in: title of book
        :param keywords_in: keywords list of book
        :param recommend_number: number of return recommendationS
        :return:
        """
        r_proportion = self.review_proportion
        i_proportion = 1 - self.review_proportion
        book_similarity = []

        # Empty Input
        if len(keywords_in) <= 0: return book_similarity

        # 각 책에 대한 loop
        for title, keywords in self.keywords.items():
            #print(f'Title in: {title_in}\n'
            #      f'Keyword in: {keywords_in}\n'
            #      f'Compare with {title}\n'
            #      f'keyword: {keywords}')
            info_keywords = keywords[Keytype.INFO.name]
            review_keywords = keywords[Keytype.REVIEW.name]     # Could be a multiple list
            sims_info = []
            sims_review = []    # 2 Dimensional List  CAUTION !!!

            # Calculate similarity: with book information
            for info_keyword in info_keywords:
                for keyword_in in keywords_in:
                    sims_info.append(self.sentence_similarity(keyword_in, info_keyword))

            # Calculate similarity: with reviews
            for review_keyword_list in review_keywords:
                for review_keyword in review_keyword_list:
                    temp_sims_review = []
                    for keyword_in in keywords_in:
                        temp_sims_review.append(self.sentence_similarity(keyword_in, review_keyword))
                    sims_review.append(temp_sims_review)

            similarity = 0

            # Calculate average similarity for each book
            if len(sims_info) != 0 and len(sims_review) != 0:

                # Calculate info similarity (simply use avg)
                info_sim_avg = sum(sims_info) / len(sims_info)

                # Calculate review similarity (simpley use avg + sorting) -> List
                review_sim_list = []
                for review_sim in sims_review:
                    avg_similarity = sum(review_sim) / len(review_sim)
                    review_sim_list.append(avg_similarity)

                    # Choose / Calculate total review similarity
                review_sim_list.sort(reverse=True) # 내림차순 정렬 ->가장 높은 유사도 활용하기 위함. 바꿀 수 있다.
                review_sim_avg = review_sim_list[0]

                # Total Similarity
                similarity = (r_proportion * review_sim_avg) + (i_proportion * info_sim_avg)

            # TODO - we can just ignore when there is no review, but now I choose to use half
            # When there is no review/info
            else:
                # To make review list without empty review
                review_except_empty = [review_sim for review_sim in sims_review if len(review_sim) != 0]

                # There is no review
                if len(sims_info) != 0:
                    similarity = sum(sims_info) / len(sims_info)

                # There is no info
                elif len(sims_review) != 0:
                    # Calculate review similarity (simpley use avg + sorting) -> List
                    review_sim_list = []
                    for review_sim in review_except_empty:
                        avg_similarity = sum(review_sim) / len(review_sim)
                        review_sim_list.append(avg_similarity)

                    # Choose / Calculate total review similarity
                    review_sim_list.sort(reverse=True)  # 내림차순 정렬 ->가장 높은 유사도 활용하기 위함. 바꿀 수 있다.
                    similarity = review_sim_list[0]

                # In case that there is no info and review (Only name of book)
                #else:
                    #print(f"WARNING: Empty Dataset\n"
                     #     f"    input title:{title_in}, keywords:{keywords_in}"
                      #    f"    current  title: {title}")

            book_similarity.append([title, similarity])

        book_similarity.sort(key=lambda x: x[1], reverse=True)
        titles = [item[0] for item in book_similarity]      # get only title, not similarity
        # print(f"titles: {titles}\nbooks: {book_similarity}")
        book_recommend = titles[:recommend_number]
        return book_recommend

    def _match_both_error(self, title: str, keywords: list, recommend_number=5):
        """
        DO NOT USE THIS METHOD
        :param title: simple string of title
        :param keywords: [keyword1, keyword2, ... ]
        :return:
        """
        # TODO 복수개의 Review 처리 안되어있음
        r_proportion = self.review_proportion
        i_proportion = 1 - self.review_proportion
        book_similarity = []
        for title, keywords in self.keywords.items():
            info_keywords = keywords[Keytype.INFO.name]
            review_keywords = keywords[Keytype.REVIEW.name]
            sims_info = []
            sims_review = []

            # Calculate similarity: with book information
            for info_keyword in info_keywords:
                for keyword in keywords:
                    sims_info.append(self.sentence_similarity(keyword, info_keyword))

            # Calculate similarity: with reviews
            for review_keyword in review_keywords:
                for keyword in keywords:
                    sims_review.append(self.sentence_similarity(keyword, review_keyword))

            similarity = 0

            # Calculate average similarity for each book
            if len(sims_info) != 0 and len(sims_review) != 0:
                info_sim_avg = sum(sims_info) / len(sims_info)
                review_sim_avg = sum(sims_review) / len(sims_review)
                similarity = (r_proportion * review_sim_avg) + (i_proportion * info_sim_avg)

            # When there is no review/info
            else:
                if len(sims_info) != 0:
                    similarity = sum(sims_info) / len(sims_info)
                elif len(sims_review) != 0:
                    similarity = sum(sims_review) / len(sims_review)

            book_similarity.append([title, similarity])

        book_similarity.sort(key=lambda x: x[1], reverse=True)
        titles = [item[0] for item in book_similarity]
        print(f"titles: {titles}\nbooks: {book_similarity}")
        book_recommend = titles[:recommend_number]
        return book_recommend

    def match_both_test(self):
        r_proportion = self.review_proportion
        i_proportion = 1 - self.review_proportion

        print(f"Match test - review[{r_proportion}] + info[{i_proportion}]")

        for i, review in enumerate(self.reviews):
            print(f'{i}: {review}')
        review_num = int(input('\nEnter review number: '))

        while 0 <= review_num <= len(self.reviews):
            review_sample = self.reviews[review_num]
            print(f'Sample review: {review_sample}')

            # TODO 복수개의 리뷰 처리 안되어있음
            recommend = self.match_both(review_sample[0], review_sample[1])
            print(f'Recommendation: {recommend}')
            review_num = int(input('\nEnter review number: '))

    def match_book2review(self, reviews, books):
        print("Match test")

        for i, line in enumerate(reviews):
            print(f'{i}: {line}')

        review_num = int(input('\nEnter review number: '))
        review_sample = reviews[0]
        while 0 <= review_num <= len(reviews):
            book_similarity = []
            review_sample = reviews[review_num]
            print(f'Sample review: {review_sample}')
            for book in books:
                title = book[0]
                keywords = book[1]
                sims = []
                #print(f'title: {title}, keywords: {keywords}')
                for keyword in keywords:
                    for review in review_sample[1]:
                        sims.append(self.sentence_similarity(review, keyword))

                book_similarity.append([title, sum(sims)/len(sims)])

            book_similarity.sort(key=lambda x: x[1], reverse=True)
            print(book_similarity)
            review_num = int(input('\nEnter review number: '))

    def match_review2review(self):
        # Use 'match_both' method with review keyword input, proportion 0:1
        pass

    def test_and_save_as_csv(self, keyword_path: str, encoding='utf-8'):
        dataframe = pd.read_csv(keyword_path, encoding=encoding)
        columns = ['title'] + [f'keyword{i}' for i in range(1, 6)] + [f'book{j}' for j in range(1, 6)]
        processed_data = []

        current_time = datetime.now().strftime(self.time_format)
        saved_file_name = f'results/match_test_{current_time}.csv'
        saved_current_keywords_name = f'results/match_test_{current_time}_keywords.csv'

        # Save input keywords and recommendation
        for index, row in dataframe.iterrows():
            title = row['title']
            keywords = [row[f'keyword{i}'] for i in range(1, 6) if pd.notnull(row[f'keyword{i}'])]
            recommendations = self.match_both(title, keywords, recommend_number=5)

            # Keyword, Recommendation 5개로 양식 맞추기 위한 파트
            keywords = (keywords + [''] * 5)[:5]
            recommendations = (recommendations + [''] * 5)[:5]

            # 합쳐서 processed_data 에 추가
            row_data = [title] + keywords + recommendations
            processed_data.append(row_data)

        output_df = pd.DataFrame(processed_data, columns=columns)
        output_df.to_csv(saved_file_name, index=False, encoding='utf-8-sig')
        
        # 현재 키워드 저장
        self._save_current_keywords(saved_current_keywords_name)

    def _save_current_keywords(self, csvpath: str):
        processed_data = []
        columns = ['title'] + [f'keyword{i}' for i in range(1, 6)]

        # TODO 복수개의 리뷰 처리 안되어있음
        for title, keywords in self.keywords.items():
            info_keyword = (keywords[Keytype.INFO.name] + [''] * 5)[:5]
            review_keyword = (keywords[Keytype.REVIEW.name] + [''] * 5)[:5]

            info_row = [f'I_{title}'] + info_keyword
            review_row = [f'R_{title}'] + review_keyword
            processed_data.append(info_row)
            processed_data.append(review_row)

        output_df = pd.DataFrame(processed_data, columns=columns)
        output_df.to_csv(csvpath, index=False, encoding='utf-8-sig')

    def save_satus_to_exit(self):
        #TODO
        pass

class Keytype(IntEnum):
    INFO = 0
    REVIEW = 1

