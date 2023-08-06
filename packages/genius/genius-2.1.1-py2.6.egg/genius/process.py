#encoding:utf-8
import re
import copy
from .trie import TrieTree
from .loader import ResourceLoader
from .tools import StringHelper
from .word import Word
from .digital import is_chinese_number, chinese_to_number


class BaseSegmentProcess(object):

    group_marker = re.compile(
        '|'.join(map(lambda x: '%s+[*?]*' % x, [
            StringHelper.digit_pattern,
            StringHelper.alpha_pattern,
            StringHelper.whitespace_pattern,
            StringHelper.halfwidth_punctuation_pattern,
            StringHelper.cjk_pattern,
        ])),
        re.UNICODE
    ).findall

    def __init__(self, **kwargs):
        self.string_helper = StringHelper()
        self.segment_type = 'marker'

    def split_by_groups(self, word, groups):
        length = len(groups)
        offset = word.offset
        words = []
        for index in range(length):
            group = groups[index]
            word = Word(group, offset=offset, source=self.segment_type)
            offset += len(group)
            words.append(word)
        return words

    def process(self, word):
        """
        将文本切割成以marker为单位的词
        """
        groups = self.group_marker(word.text)
        return self.split_by_groups(word, groups)


class SimpleSegmentProcess(BaseSegmentProcess):

    def __init__(self, **kwargs):
        BaseSegmentProcess.__init__(self, **kwargs)
        self.loader = ResourceLoader()
        self.seg_model = self.loader.load_crf_seg_model()
        self.segment_type = 'crf'

    def process(self, word):
        words = BaseSegmentProcess.process(self, word)
        pre_words = []
        for word in words:
            if word.marker == 'CJK':
                label = self.label_sequence(word.text)
                groups = self.segment(label, word.text)
                pre_words.extend(self.split_by_groups(word, groups))
            else:
                pre_words.append(word)
        return pre_words

    def label_sequence(self, text, nbest=1):
        if self.seg_model.options.nbest != nbest:
            self.seg_model.options.nbest = nbest
        label = self.seg_model.label_sequence(
            '\n'.join(text), False).decode('utf-8')
        return label.strip(self.string_helper.whitespace_range)

    @classmethod
    def segment(cls, label, text):
        result_words = []
        offset = 0
        for index, label in enumerate(label.split('\n')):
            if 'S' == label:
                if index - offset > 1:
                    result_words.append(text[offset:index])
                result_words.append(text[index])
                offset = index + 1
            elif 'E' == label:
                result_words.append(text[offset:index + 1])
                offset = index + 1
        if offset < len(text):
            result_words.append(text[offset:])
        return result_words


class KeywordsSegmentProcess(SimpleSegmentProcess):

    def __init__(self, **kwargs):
        SimpleSegmentProcess.__init__(self, **kwargs)

    def process(self, word):
        length = len(word.text)
        if length <= 3:
            return self.crf_keywords(word, nbest=1)
        else:
            return self.crf_keywords(word, 2)

    def crf_keywords(self, word, nbest=2):
        words = BaseSegmentProcess.process(self, word)
        pre_words = []
        for word in words:
            if word.marker == 'CJK':
                labels = self.label_sequence(word.text, nbest).split('\n\n')
                words_list = filter(
                    lambda x: x,
                    [self.split_by_groups(
                        word, self.segment(label, word.text)
                    ) for label in labels],
                )
                pre_words.extend(
                    self.split_by_groups_keywords(word.text, words_list))
            else:
                pre_words.append(word)
        return pre_words

    @classmethod
    def split_by_groups_keywords(cls, text, words_list):
        trie = TrieTree()
        for words in words_list:
            for word in words:
                trie[word.text] = word
        pos, length = 0, len(text)
        pre_words = []
        while pos < length:
            dic = trie.search(text[pos:])
            for i in range(pos + 1, length + 1):
                word = text[pos:i]
                if word in dic:
                    pre_words.append(dic[word])
            pos += 1
        return pre_words


class PinyinSegmentProcess(BaseSegmentProcess):

    def __init__(self, **kwargs):
        BaseSegmentProcess.__init__(self, **kwargs)
        self.loader = ResourceLoader()
        self.trie = self.loader.load_trie_tree()
        self.segment_type = 'pinyin'

    def process(self, words):
        pre_words = []
        for word in words:
            if word.marker == 'ALPHA':
                pinyins = self.segment(word.text)
                if pinyins:
                    pre_words.extend(self.split_by_groups(
                        word, pinyins))
                else:
                    pre_words.append(word)
            else:
                pre_words.append(word)
        return pre_words

    def segment(self, text):
        length = len(text)
        pos = 0
        pre_words = []
        while pos < length:
            dic = self.trie.search(text[pos:length])
            max_matching_pos = 0
            for i in range(pos + 1, length + 1):
                if text[pos:i] in dic:
                    max_matching_pos = i
            if max_matching_pos == 0:
                return None
            else:
                pinyin = text[pos:max_matching_pos]
                pre_words.append(pinyin)
            pos = max_matching_pos
        return pre_words


class BreakSegmentProcess(BaseSegmentProcess):

    def __init__(self, **kwargs):
        BaseSegmentProcess.__init__(self, **kwargs)
        self.loader = ResourceLoader()
        self.tree = self.loader.load_break_table()
        self.segment_type = 'break'

    def process(self, words):
        break_word_result = []
        for word in words:
            if word.text in self.tree:
                break_word_result.extend(
                    self.split_by_groups(word, self.tree[word.text]))
            else:
                break_word_result.append(word)
        return break_word_result


class CombineSegmentProcess(BaseSegmentProcess):

    def __init__(self, **kwargs):
        BaseSegmentProcess.__init__(self, **kwargs)
        self.loader = ResourceLoader()
        self.trie = self.loader.load_trie_tree()
        self.combine_regex_method = self.loader.load_combine_regex_method()

    def process(self, words):
        pos = 0
        length = len(words)
        pre_words = []
        while pos < length:
            max_matching_pos = 0
            dic = self.trie.search(''.join(
                map(lambda x: x.text, words[pos:length])))
            for i in range(pos + 1, length + 1):
                text = ''.join(map(lambda x: x.text, words[pos:i]))
                if text in dic:
                    max_matching_pos = i
                elif is_chinese_number(text) and chinese_to_number(text):
                    max_matching_pos = i
                elif self.combine_regex_method(text):
                    max_matching_pos = i
            if max_matching_pos == 0:
                max_matching_pos = pos + 1
            text = ''.join(map(lambda x: x.text, words[pos:max_matching_pos]))
            word = words[pos]
            if text in dic:
                pre_word = copy.copy(dic[text])
                pre_word.offset = word.offset
                word = pre_word
            elif max_matching_pos == pos + 1:  # 无匹配
                word = words[pos]
            else:
                word = Word(text)
                word.offset = word.offset
            pre_words.append(word)
            pos = max_matching_pos
        return pre_words


class TaggingProcess(object):

    def __init__(self, **kwargs):
        self.string_helper = StringHelper()
        self.loader = ResourceLoader()
        self.tagging_model = self.loader.load_crf_pos_model()

    def label_tagging(self, words):
        if self.tagging_model.options.nbest != 1:
            self.tagging_model.options.nbest = 1
        label_sequence_texts = []
        unlabel_sequence_indexes = []
        for index, word in enumerate(words):
            if word.marker == 'WHITESPACE':
                unlabel_sequence_indexes.append(index)
            else:
                label_sequence_texts.append(
                    u'%s\t%s' % (word.text, word.marker))
        label_text = self.tagging_model.label_sequence(
            '\n'.join(label_sequence_texts),
            include_input=False,
        ).strip(self.string_helper.whitespace_range)
        taggings = label_text.split('\n')
        map(lambda x: taggings.insert(x, 'x'), unlabel_sequence_indexes)
        return taggings

    def process(self, words):
        taggings = self.label_tagging(words)
        for index, word in enumerate(words):
            if word.marker == 'DIGIT':
                word.tagging = 'm'
            elif word.marker == 'ALPHA':
                word.tagging = 'en'
            elif word.marker == 'PUNC':
                word.tagging = 'w'
            else:
                word.tagging = taggings[index]
        return words

    @classmethod
    def tagging(cls, label):
        taggings = []
        for word_label in filter(lambda x: x, label.split('\n')):
            tagging = word_label.decode('utf-8')
            taggings.append(tagging)
        return taggings


processes = {
    'default': SimpleSegmentProcess,
    'break': BreakSegmentProcess,
    'combine': CombineSegmentProcess,
    'pinyin_segment': PinyinSegmentProcess,
    'segment_keywords': KeywordsSegmentProcess,
    'tagging': TaggingProcess,
}
