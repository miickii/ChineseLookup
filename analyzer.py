import jieba
import jieba.posseg as posseg # For splitting sentences
from wordfreq import word_frequency
import os.path
import re

class Analyzer:
    def __init__(self):
        self.jieba_dict_path = os.path.join(os.path.dirname(__file__), "files/jieba_dict.txt")
        self.load_dict()
        self.common_words = ['零', '四', '五', '六', '七', '八', '九', '十', '千', '百', '学生', '至', '那么', '那麽', '钱', '一定', '不同', '电影', '万', '不要', '使', '像', '点', '只是', '听', '这么', '这麽', '关系', '出来', '此', '起', '任何', '两', '自', '这里', '一起', '因此', '国', '如', '带', '走', '有了', '中心', '人们', '今天', '吃', '岁', '无', '而且', '话', '一直', '家', '区', '城市', '太', '市场', '最后', '约', '么', '麽', '之后', '问', '东西', '特别', '开', '中的', '大学', '学校', '朋友', '目前', '站', '不在', '一种', '元', '因', '孩子', '安全', '写', '成', '关于', '大家', '打', '运动', '部分', '分', '死', '见', '非常', '叫', '曾', '有人', '买', '参加', '当时', '过去', '那些', '即', '卽', '单位', '完全', '得到', '有关', '生产', '产品', '道', '天', '然后', '总', '那个', '一切', '人口', '应', '正', '无法', '进入', '我人', '上海', '便', '个人', '间', '干', '名', '完成', '本', '发', '对了', '一点', '找', '不和', '你我', '事件', '您', '玩', '受', '准备', '真', '进', '之间', '事情', '哪里', '女', '学习', '成功', '每', '种', '英国', '市', '接受', '正在', '一下', '以后', '作', '有些', '网', '老', '认识', '之前', '原因', '外', '女人', '专业', '小时', '科学', '多少', '感觉', '举行', '艺术', '电话', '马', '机会', '美', '行', '韩国', '有年', '拿', '它们', '手机', '法国', '这不', '为人', '仍', '同', '哪', '严重', '帮助', '台', '工业', '第一', '到了', '中人', '不对', '二', '住', '学', '怎样', '男人', '非', '别', '只要', '回', '才能', '书', '以下', '我国', '以上', '年代', '几个', '心', '的话', '一个人', '之一', '的', '是', '在', '了', '我', '和', '有', '不', '人', '也', '你', '为', '他', '这', '中', '年', '与', '对', '就', '都', '上', '说', '吗', '我们', '到', '会', '要', '来', '中国', '月', '被', '他们', '没有', '还', '而', '个', '可以', '后', '等', '但', '于', '於', '什么', '日', '这个', '并', '将', '能', '一', '很', '让', '国家', '从', '以', '好', '大', '她', '着', '多', '自己', '问题', '时', '给', '把', '去', '看', '又', '美国', '或', '因为', '下', '不是', '之', '现在', '过', '新', '里', '做', '及', '地', '由', '是的', '怎么', '没', '用', '就是', '已经', '更', '这些', '得', '所', '最', '想', '发展', '这样', '开始', '公司', '它', '政府', '可能', '那', '工作', '社会', '三', '可', '吧', '如果', '知道', '进行', '世界', '其', '日本', '该', '不能', '只', '向', '计划', '前', '成为', '时间', '认为', '需要', '出', '啊', '已', '再', '当', '国际', '地区', '小', '时候', '却', '们', '内', '使用', '才', '经济', '爱', '活动', '但是', '应该', '政治', '历史', '第', '谁', '不会', '以及', '情况', '组织', '了了', '人民', '其他', '发生', '主要', '地方', '网站', '号', '香港', '生活', '这种', '你们', '通过', '事', '同时', '必须', '快', '为了', '有的', '所以', '所有', '比', '跟', '包括', '发现', '请', '还有', '长', '一些', '全国', '出现', '呢', '如何', '决定', '为什么', '还是', 'A', '一样', '企业', '其中', '北京', '觉得', '重要', '高', '影响', '则', '喜欢', '文化', '起来', '不过', '作为']
    
    def load_dict(self):
        """
        Load dictionary
        """
        if not os.path.exists(self.jieba_dict_path):
            print("jieba dictionary not found")
            return

        jieba.load_userdict(self.jieba_dict_path)

    # Get Parts Of Speech for word
    def get_word_pos(self, word):
        words = posseg.cut(word)
        flags = []
        for w in words:
            flags.append(w.flag)

        if len(flags) == 1:
            return flags[0]
        
        return ""
    
    def get_word_freq(self, word):
        return word_frequency(word, 'zh')
    
    # Splits a chinese text into individual words
    def tokenize(self, text):
        return [tk for tk in jieba.lcut(text, cut_all=False) if (tk not in ' 。，“”--：；')]
    
    # Splits chinese word into each seperate character, returns array where first element is the word and second is the list of characters
    def split_characters(self, word):
        # Some words in the HSK database also has example usage in parenthesis, which should be ignored.
        # only_word = word.split('（')[0]
        only_word = re.split(r'[(（]', word)[0].strip()
        return [only_word, [c for c in only_word]]
    
    # Takes in a list of chinese words from database and orders them by their frequency
    def sort_words_by_freq(self, words):
        frequencies = [w['frequency'] for w in words]
        
        # for w in words:
        #     freq = self.get_word_freq(w)
        #     frequencies.append(freq if freq else 0)
        
        # Here sorted returns the indicies to frequencies after it's sorted
        # range(len(frequencies)) is an iterable that loops over length of the frequencies list
        # key is a function. This function takes the value from the iterable and returns a transformed value.
        # Its the transformed values that get's sorted
        # .__getitem__ is a magic method that gives the value at an index. If the range iterable is at 2, __getitem__ would return frequencies[2]
        indicies = sorted(range(len(frequencies)), key=frequencies.__getitem__, reverse=True) # reverse because we want the highest score to be first
        # ALTERNATIVELY: sorted(range(len(s)), key=lambda k: s[k])

        # PRINTING ORDERED FREQUENCIES
        # for i in range(len(words)):
        #     print(words[i]['chinese'] + "   " + str(frequencies[i]))
        # With the indicies list we can now get the sorted sequence for words as well as their frequencies
        return [words[i] for i in indicies]

    def chinese_words_from_text(self, text):
        words = []

        # split the text on .,，, and 。 characters and remove them
        splitted_text = re.split('[,.，。!•]', text)

        # remove empty strings from the list
        splitted_text = list(filter(None, splitted_text))

        for t in splitted_text:
            only_chinese = re.sub(r'[^\u4e00-\u9fff]', ' ', t).strip()
            chinese = only_chinese.split(" ")
            chinese = list(filter(None, chinese))
            
            for c in chinese:
                words.extend(jieba.lcut(c, cut_all=False))
        
        return words

    def frequency_list_from_text(self, text, exclude_common_words=True):
        words = self.chinese_words_from_text(text)

        word_amount = len(words)
        count = {}

        for word in words:
            if word not in count:
                count[word] = 1
            else:
                count[word] += 1
        
        freq_list = sorted(count, key=count.get, reverse=True)
        percentage_list = []
        for word in freq_list:
            percentage = count[word] / word_amount * 100
            percentage_list.append(percentage)
            print(word, percentage)

        if exclude_common_words:
            freq_list = [word for word in freq_list if (word not in self.common_words)]
        
        return freq_list
    
        