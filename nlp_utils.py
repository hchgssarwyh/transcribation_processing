from typing import List
from sentence_transformers import SentenceTransformer, util
import spacy
from openai import OpenAI



class SentenceTransformersSimilarity():
    def __init__(self, similarity_threshold, model='sergeyzh/rubert-tiny-turbo'):
        self.model = SentenceTransformer(model)
        self.similarity_threshold = similarity_threshold

    def similarities(self, sentences: List[str]):
        # Encode all sentences
        embeddings = self.model.encode(sentences)

        # Calculate cosine similarities for neighboring sentences
        similarities = []
        for i in range(1, len(embeddings)):
            sim = util.pytorch_cos_sim(embeddings[i-1], embeddings[i]).item()
            similarities.append(sim)

        return similarities
    

class SimilarSentenceSplitter():
    def __init__(self, similarity_model):
        self.model = similarity_model
        self.nlp = spacy.load('ru_core_news_sm')  # Загружаем модель spaCy для русского языка

    def split(self, texts: List[str], group_max_sentences=5) -> List[List[str]]:
        '''
            texts: List of texts (each text is a string), each text will be processed separately.
            group_max_sentences: The maximum number of sentences in a group.
        '''
        all_groups = []  # Хранит группы для всех текстов

        for text in texts:
            # Используем spaCy для токенизации предложений
            doc = self.nlp(text)
            sentences = [sent.text for sent in doc.sents]

            if len(sentences) == 0:
                continue

            similarities = self.model.similarities(sentences)

            # Первое предложение всегда в первой группе
            groups = [[sentences[0]]]

            # Группировка предложений на основе их схожести и ограничений по количеству
            for i in range(1, len(sentences)):
                if len(groups[-1]) >= group_max_sentences:
                    groups.append([sentences[i]])
                elif similarities[i-1] >= self.model.similarity_threshold:
                    groups[-1].append(sentences[i])
                else:
                    groups.append([sentences[i]])

            # Объединяем предложения в каждой группе в одну строку
            combined_groups = [' '.join(group) for group in groups]

            all_groups.append(combined_groups)

        return all_groups

class LLMTagGenerator():
    def __init__(
        self,
        api_key: str,
        base_url= 'https://api.vsegpt.ru/v1',

    ) -> None:
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        ),
        self.model = SentenceTransformer('sergeyzh/rubert-tiny-turbo'),
    def generate_tags(self, video_description: str):
        prompt = f"Сгенерируй список тегов по следующему описанию видео: \"{video_description}\". Теги должны быть разделены запятой."
        messages = []
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=50,  # Limit on the number of tokens in the response
            n=1,            # Number of responses
            stop=None,      # Stopping condition
        )
        tags = response.choices[0].message.content
        return [tag.strip() for tag in tags.split(',')]
    

    def get_embedding(self, texts):
    # Получаем эмбеддинги для списка текстов (массивы преобразуются один раз)
        return self.model.encode(texts, convert_to_tensor=True)

    def cosine_similarity_matrix(embeddings1, embeddings2):
        # Используем pytorch для нахождения косинусного сходства сразу между всеми векторами
        return util.pytorch_cos_sim(embeddings1, embeddings2)  # Возвращает матрицу схожести

    def get_target_tags(self, given_tags_list, target_tags, threshold=0.85):
        # Предварительно рассчитываем эмбеддинги для всех target тегов
        target_embeddings = self.get_embedding(target_tags)

        ans = set()  # Используем множество для уникальных тегов
        for given_tags in given_tags_list:  # Проходим по каждому списку тегов
            # Получаем эмбеддинги для текущего списка тегов
            given_embeddings =  self.get_embedding(given_tags)

            # Вычисляем матрицу косинусных сходств между всеми предложенными и разрешенными тегами
            similarity_matrix =  self.cosine_similarity_matrix(given_embeddings, target_embeddings)

            # Ищем схожие теги на основе порога
            for i, given_tag in enumerate(given_tags):
                for j, target_tag in enumerate(target_tags):
                    similarity = similarity_matrix[i, j].item()  # Извлекаем значение схожести
                    if similarity > threshold:
                        ans.add(target_tag)  # Добавляем совпавший тег из разрешенных, который является строкой
                        print(f'{given_tag} -> {target_tag}: {similarity}')
        return ans