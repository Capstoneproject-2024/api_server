from tokenize import group
from gensim.models import fasttext
import numpy as np
from FileReader import *
from enum import IntEnum
from datetime import datetime
import math


class Matcher:
    def __init__(self, modelpath='models/cc.ko.300.bin.gz', use_model=True):
        # TODO 실제 배포 전 아래 3개의 리스트는 set keyword시 초기화 할 것 -> 현재 DATA -> CSV 저장을 위해 초기화하지 않음
        self.books = []
        self.reviews = []
        self.vocabs = []

        if use_model:
            self.model = fasttext.load_facebook_vectors(modelpath)

        self.reader = Filereader()
        self.review_proportion = 0.5    # Proportion of Review
        self.time_format = "%y%m%d-%H%M%S"
        self.vocab_weight = 1.5
        
        # NOTICE!: book_title -> book_id = 'int', book_title = 'string', DB 에서 무엇을 받아 오느냐에 따라 달라짐
        self.keywords = {}              # { book_title: {info: [], review: [], vocab: []}} Caching the keywords for testing
        # self.keywords_categorized = {}  # { Keyword_category: [book1, book2, ...], Keyword_category: [...] }
        self.group_vocab = []

        self.initialize_group_vocab()
        self.set_keywords()
        print("SimMatcher.py: sim_matcher ready")

# Print Functions ======================================================================================
    def print_all_keywords(self):
        print("------------------------------------------------------------")
        for title, keywords in self.keywords.items():
            print(f'Title: "{title}", {type(title)}\n'
                  f'Info Keywords  : {keywords[Keytype.INFO.name]}, {Keytype.INFO.name}\n'
                  f'Review Keywords: {keywords[Keytype.REVIEW.name]}, {Keytype.REVIEW.name}\n'
                  f'Group Vocab    : {keywords[Keytype.VOCAB.name]}, {Keytype.VOCAB.name}\n')
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

# Setter Functions ======================================================================================
    def initialize_temporary_lists(self):
        self.books = []
        self.reviews = []
        self.vocabs = []

    def set_vocab_weight(self, weight):
        self.weight = weight

    def set_keywords(self,
                     book_keyword_path='BookInfo.txt',
                     review_keyword_path='data/keywords/POS_before_extraction.csv'):
        """
        Load keywords from review and book information files.
        Only for testing level. It should be replaced with DB API.
        :param book_keyword_path:
        :param review_keyword_path:
        :return:
        """

        """
        WARNING: If we try to get data from API, we should get both review and books
                from API. API use book_id as a title.
        """
        #self.getBooks(book_path=book_keyword_path)
        # Change for select review file { Json / CSV }
        #self.getReviews_csv(review_path=review_keyword_path)
        #self.getBooks(book_path=book_keyword_path)
        self.getReviews_API()
        self.getBooks_API()
        self.getBookVocab_API()

        for book in self.books:
            self._add_keyword(str(book[0]), book[1], Keytype.INFO)       # [0] = title, [1] = info (List[STR])

        for review in self.reviews:
            self._add_keyword(str(review[0]), review[1], Keytype.REVIEW)  # [0] = title, [1] = review keywords (List[str])

        for vocab in self.vocabs:
            self._add_keyword(str(vocab[0]), vocab[1], Keytype.VOCAB)     # [0] = title, [1] = Vocab (STR)

        print("SimilarityMatcher.py: Keywords set")
        self.initialize_temporary_lists()

    def _add_keyword(self, title: str, keywords, key_type: int):
        if title not in self.keywords:
            self.keywords[title] = {Keytype.INFO.name: [], Keytype.REVIEW.name: []}

        # Review
        if key_type == Keytype.REVIEW and keywords not in self.keywords[title][Keytype.REVIEW.name]:
            self.keywords[title][Keytype.REVIEW.name].append(keywords)

        # Book Info
        elif key_type == Keytype.INFO:
            self.keywords[title][Keytype.INFO.name] = keywords

        # Group Vocab
        elif key_type == Keytype.VOCAB:
            self.keywords[title][Keytype.VOCAB.name] = keywords

# Similarity Functions ======================================================================================
    def _s2v_mean(self, sentence: str, voo='similar'):
        """
        Calculate vector of a single sentence using arithmetic mean
        splitting the sentence
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

# Data Getting Functions ======================================================================================
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

    def getBookVocab_API(self):
        self.vocabs = self.reader.get_book_vocab()

    def initialize_group_vocab(self):
        gv = self.reader.get_group_vocab()
        self.group_vocab = gv

# Group Vocab Functions =========================================================================================

    def match_group_vocab(self, keywords: list[str]) -> str:
        """
        Get keywords, return group word
        :param keywords: POS PROCESS HAVE TO BE DONE!!!!
        :return:
        """
        gk_pool = self.group_vocab

        keyword_group_similarity = []

        for g_key in gk_pool:
            group_word_similarity = [g_key]
            similarities = [self.sentence_similarity(g_key, key) for key in keywords]
            group_word_similarity.append(np.average(similarities))
            # -> group_word_similarity = [g_key, average_similarity]

            keyword_group_similarity.append(group_word_similarity)

        keyword_group_similarity.sort(key=lambda x: x[1], reverse=True)
        group_words = [item[0] for item in keyword_group_similarity]        # get only title, not similarity
        recommend_gw = group_words[0]
        return recommend_gw

# Keyword Matching Functions ======================================================================================
    def set_proportion(self, review_proportion: int):
        if 0 <= review_proportion <= 100:
            self.review_proportion = review_proportion/100
        else:
            print("WARNING: Proportion should be in 0~100")

    def match_quot(self, title_in: str, quot_keywords: list, book_list: list, vocab ='', only_quot=False):
        """
        Have to test the extraction of quotation
        Use [top-3 book keyword | top-3 quot_keyword]
        :param only_quot: param to choose using past book list (False) or not (True)
        :param vocab:
        :param title_in:
        :param quot_keywords:
        :param book_list:
        :return:
        """
        quot_keywords_in = quot_keywords

        # TODO Get keywords of books using db api -> created via 'book_list' input
        # TODO 가정 : book_list에는 str형태로 읽은 책의 list가 들어온다.
        #book_keywords = [['제목1', ['책키11', '책키12', '책키13', '책키14', '책키15']],
        #                 ['제목2', ['책키21', '책키22', '책키23', '책키24', '책키25']],
        #                 ['제목3', ['책키31', '책키32', '책키33', '책키34', '책키35']],
        #                 ['제목4', ['책키41', '책키42', '책키43', '책키44', '책키45']],
        #                 ['제목5', ['책키51', '책키52', '책키53', '책키54', '책키55']]]

        book_keywords = []
        for book in book_list:
            book_keywords.append([book, self.keywords[book][Keytype.INFO.name]])


        # 읽은 책이 1권 이하일 경우 선정 과정 생략
        book_keyword_flag = True
        selected_book_keywords = book_keywords[0]        # Selected book keywords is a single '1' book in book_keywords

        # 책 0권 -> 에러로 판단
        if book_list in None or len(book_list) < 1:
            print('Sim_Matcher: match-quot get null book list, return None')
            return None

        # 책 선정 - 1 권
        if len(book_list) == 1:
            book_keyword_flag = False

        # 책 선정 - 여러 권인 경우
        if book_keyword_flag and not only_quot:
            # Keyword 벡터로 변환한 리스트 만들기 -> [title, average_vector] 의 리스트
            book_vectors = []
            for title, keywords in book_keywords:
                keyword_vector = [self._s2v_mean(key) for key in keywords]
                book_vectors.append([title, np.mean(keyword_vector, axis=0)])

            # Book input 간 유사도 계산 -> 전체를 대표할 수 있는지 평균 유사도 이용해 측정
            book_similarities = []
            for i, (title_i, vector_i) in enumerate(book_vectors):
                similarities = []
                for j, (title_j, vector_j) in enumerate(book_vectors):
                    if i != j:
                        sim = self._cosine_similarity(vector_i, vector_j)
                        similarities.append(sim)
                # 평균 유사도 계산
                average_similarity = np.mean(similarities)
                book_similarities.append((title_i, average_similarity))

            selected_book_title = max(book_similarities, key=lambda x: x[1])[0]
            for i, book in enumerate(book_list):
                if book[0] == selected_book_title:
                    selected_book_keywords = book_keywords[i]

        # 두 가지 키워드 절반씩 합치기 (인용구, 책)
        aggregated_keywords = []
        if only_quot:
            aggregated_keywords.extend(quot_keywords_in)
        else:
            aggregated_keywords.extend(quot_keywords_in[:math.ceil(len(quot_keywords_in)/2)])
            aggregated_keywords.extend(selected_book_keywords[:math.ceil(len(selected_book_keywords)/2)])

        # Match
        recommendation = self.match_both(title_in, aggregated_keywords, vocab=vocab)
        return recommendation

    def match_q2q(self, title_in: str, quot_keywords: list, book_list: list, vocab = 'gw'):
        """
        get Quotation, match with other Quotations only
        Process: 1. calculate average Sentence Vector of quotation
                 2. Compare with other quotations -> (n x n) full-compare for each quotation -> O(n^3)
                 3. Sort for each quotation -> can get recommendation for each quotation
        :param vocab:
        :param title_in:
        :param quot_keywords:
        :param book_list:
        :param g_word:
        :return:
        """
        # TODO
        pass

    def match_both(self, title_in: str, keywords_in: list, vocab: str = '', recommend_number=5):
        """
        :param vocab:
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

            if title == title_in: continue                      # Skip if title == input_title

            info_keywords = keywords[Keytype.INFO.name]
            review_keywords = keywords[Keytype.REVIEW.name]     # Could be a multiple list
            book_vocab = keywords[Keytype.VOCAB.name]
            sims_info = []
            sims_review = []    # 2 Dimensional List  CAUTION !!!

            # Calculate similarity: with book information
            if i_proportion > 0:
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
            
            # TODO Group vocab 같으면 가중치 추가, 디폴트값 (무시) 를 지정해야함. 현재는 Null String
            if vocab != '':
                if book_vocab == vocab:
                    similarity = similarity * self.vocab_weight
                    
            book_similarity.append([title, similarity])
        
            
        
        book_similarity.sort(key=lambda x: x[1], reverse=True)
        titles = [item[0] for item in book_similarity]      # get only title, not similarity
        # print(f"titles: {titles}\nbooks: {book_similarity}")
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

            recommend = self.match_both(review_sample[0], review_sample[1])
            print(f'Recommendation: {recommend}')
            review_num = int(input('\nEnter review number: '))

    # Do Not Use This
    def _match_both_error(self, title: str, keywords: list, recommend_number=5):
        """
        DO NOT USE THIS METHOD
        :param title: simple string of title
        :param keywords: [keyword1, keyword2, ... ]
        :return:
        """
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

    # Do Not Use This
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

    # Do Not Use This
    def match_review2review(self):
        # Use 'match_both' method with review keyword input, proportion 0:1
        pass

# Keyword Data Saving Functions ======================================================================================
    def save_group_vocab(self, encoding='utf-8-sig'):
        #TODO Group Vocab DB 연동을 위한 임시 함수. 배포 전 반드시 지운 후, self.books, self.reviews, self.vocab 초기화 할것
        columns = ['book_id', 'group_vocab']
        data = []
    
        for book, keyword_list in self.books:
            group_vocab = self.match_group_vocab(keyword_list)
            data.append([book, group_vocab])

        output_df = pd.DataFrame(data, columns=columns)
        output_df.to_csv('results/group_vocab.csv', index=False, encoding='utf-8-sig')


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
        self.reader.exit()

# Others

class Keytype(IntEnum):
    # Enum for use keyword dictionary self.keywords
    INFO = 0
    REVIEW = 1
    VOCAB = 2
