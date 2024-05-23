# -*- coding: utf-8 -*-

import random
import re
import pandas as pd
import jieba.posseg as psg
import model.translate as translate

class CBase(object):

	def __init__(self, word) -> None:
		self.modeType = ""
		self.word1 = ""
		self.shortWord1 = ""
		self.wordType1 = ""
		self.valRange1 = []
		self.valMean1 = []
		self.word2 = ""
		self.shortWord2 = ""
		self.wordType2 = ""
		self.valRange2 = []
		self.valMean2 = []
		self.steps = [random.randint(1, 5) for i in range(5)]
		self.num = random.randint(1, 10)
		self.left = random.randint(1, 3)
		self.right = random.randint(self.left + 2, self.left + 10)
		self.built(word)
		self.custombuilt(word)
		self.shortWord1 = self.wordcut(self.shortWord1, self.word1)
		self.shortWord2 = self.wordcut(self.shortWord2, self.word2)
		if self.shortWord1 == self.shortWord2:
			self.shortWord1 += self.word1[:2]
			self.shortWord2 += self.word2[:2]
		if self.valRange1:
			self.num = self.valRange1[random.randint(0, len(self.valRange1) - 1)]
			self.left = min(self.valRange1)
			self.right = max(self.valRange1)

	def __str__(self):
		return self.question() + '\n' + self.answer()

	def question(self):
		return ""


	def answer(self):
		return ""

	def wordcut(self, shortWord, word):
		wordList = [(w, c) for w, c in psg.cut(word)]
		preWordList = []
		posWordList = []
		for w, c in wordList:
			if w in ["列表",]:
				continue
			if c == "eng":
				preWordList.append(w)
			elif c == "n":
				posWordList.append(w)
		if shortWord:
			return " ".join(preWordList[:2]) + shortWord
		return " ".join(preWordList[:2]) + "".join(posWordList[:2])

	def built(self, word):
		wordList = re.split(r';|；', word)
		for i in range(len(wordList)):
			tagList = re.split(r',|，', wordList[i])
			setattr(self, f'word{i+1}', tagList[0])
			for tag in tagList[1:]:
				if tag.startswith("$"):
					count = tag.rfind("$") + 1
					for j in range(i, i + count):
						setattr(self, f'shortWord{j+1}', tag[count:])
				elif tag.startswith("&"):
					setattr(self, f'wordType{i+1}', tag[1:])
				elif "-" in tag:
					self.analyza_val(tag, i+1)
			if not getattr(self, f'wordType{i+1}', ""):
				if tagList[0].endswith("列表"):
					setattr(self, f'wordType{i+1}', "数组类型")
				elif tagList[0].endswith("状态"):
					setattr(self, f'wordType{i+1}', "整数类型")
	def custombuilt(self, word):
		self.word = self.word1
		self.shortWord = self.shortWord1
		self.wordType = self.wordType1

	def output(self):
		return pd.DataFrame({"问题":[self.question(), ], "答案":[self.answer(), ], "能力":[self.modeType, ]})

	def analyza_val(self, tag, index):
		valList = tag.split("-")
		valRange, valMean = [], []
		valType = ""
		for val in valList:
			if "_" in val:
				val, mean = tuple(val.split("_"))
				if val.isdigit():
					valType = "整数型"
				else:
					valType = "字符串型"
				valRange.append(val)
				valMean.append(mean)
			else:
				valRange.append(val)
		if len(valRange) == 2 and valRange[0].isdigit() and valRange[1].isdigit():
			valRange = [i for i in range(int(valRange[0]), int(valRange[1])+1)]
			valType = "整数型"
		else:
			valType = "字符串型"
		setattr(self, f'valRange{index}', valRange)
		setattr(self, f'valMean{index}', valMean)
		setattr(self, f'wordType{index}', valType)

class CCompVal(CBase):

	def custombuilt(self, word):
		self.modeType = "数据分析"
		self.comMode = random.randint(1, 4)
		self.word = self.word1
		self.strMode = {
			1: ("小于", "<"), 2: ("大于等于", ">="), 3: ("大于", ">"), 4: ("小于等于", "<=")
		}

	def output(self):
		seriesList = []
		for i in range(2):
			self.comMode = random.randint(1, 4)
			word = getattr(self, f'word{i+1}', "")
			if not word:
				continue
			self.word = word
			self.num = random.randint(0, 10)
			self.steps = [random.randint(1, 5) for i in range(5)]
			seriesList.append(pd.Series({"问题":self.question(), "答案":self.answer(), "能力":self.modeType}))
		return pd.concat(seriesList, axis=1).transpose()

	def question(self):
		comStr1 = self.strMode[self.comMode][0]
		if random.randint(0, 2) != 0:
			comstr2 = self.strMode[self.comMode-1][0] if self.comMode % 2 == 0 else self.strMode[self.comMode+1][0]
			comstr2 = f'如果{self.word}值{comstr2}{self.num}'
		else:
			comstr2 = "否则"
		return f'分析{self.word}的数值，{self.word}为整数型：\n如果{self.word}值{comStr1}{self.num}, 执行步骤{self.steps[0]}\n{comstr2}, 结束'

	def answer(self):
		comStr1 = self.strMode[self.comMode][1]
		comstr2 = self.strMode[self.comMode-1][1] if self.comMode % 2 == 0 else self.strMode[self.comMode+1][1]
		return f'if {translate.TranslateC(self.word)}{comStr1}{self.num}: to “{self.steps[0]}”\nif {translate.TranslateC(self.word)}{comstr2}{self.num}: to "stop"'

class CRangeVal(CBase):

	def question(self):
		return f'根据{self.word}数值分析，{self.word}为整数型：\n如果{self.word}大于{self.left}并且{self.word}小于{self.right}，执行步骤{self.steps[0]},否则，结束'

	def answer(self):
		return f'if {self.shortWord}>{self.left} and {self.shortWord}<{self.right}: to "{self.steps[0]}"\nif {self.shortWord}<={self.left} or {self.shortWord}>={self.right}: to "stop"'

class CSingleList(CBase):

	def custombuilt(self, word):
		self.strMode = random.randint(1,4)
		self.word = self.word1
		self.shortWord = self.shortWord1
		if self.shortWord1 in self.word1:
			index = random.randint(0,1)
		else:
			index = 2
		self.index = index

	def output(self):
		seriesList = []
		for i in range(2):
			word = getattr(self, f'word{i+1}', "")
			shortWord = getattr(self, f'shortWord{i+1}', "")
			if not word:
				continue
			self.strMode = random.randint(1,4)
			self.word = word
			self.shortWord = shortWord
			self.num = random.randint(0, 10)
			self.steps = [random.randint(1, 5) for i in range(5)]
			seriesList.append(pd.Series({"问题":self.question(), "答案":self.answer(), "能力":self.modeType}))
		return pd.concat(seriesList, axis=1).transpose()
	def question(self):
		questions = [f"根据查询的{self.word}的结果分析，{self.word}为数组类型：\n如果{self.word}数量为1，执行步骤{self.steps[0]}\n如果{self.word}数量不为1,结束",
			   f'对{self.word}数据分析，{self.word}为数组类型\n如果{self.word}数量为1，结束\n如果{self.word}数量不为1，执行步骤{self.steps[0]}',
			   f'检查{self.word}信息, {self.word}是数组类型:\n如果{self.word}存在{self.shortWord}，结束\n如果{self.word}不存在{self.shortWord}，执行步骤{self.steps[0]}']
		return questions[self.index]

	def answer(self):
		answers = [f'if len({translate.TranslateC(self.shortWord)})==1: to "{self.steps[0]}"\nif len({translate.TranslateC(self.shortWord)})!=1: to "stop"',
				f'if len({translate.TranslateC(self.shortWord)})==1: to "stop"\nif len({translate.TranslateC(self.shortWord)})!=1: to "{self.steps[0]}"',
				f'if len({translate.TranslateC(self.shortWord)})==1: to "stop"\nif len({translate.TranslateC(self.shortWord)})!=1: to "{self.steps[0]}"'
			]
		return answers[self.index]

class CDoubleList(CBase):

	def common_substring(self, s1, s2):
		m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
		longest, x_longest = 0, 0
		for x in range(1, 1 + len(s1)):
			for y in range(1, 1 + len(s2)):
				if s1[x - 1] == s2[y - 1]:
					m[x][y] = m[x - 1][y - 1] + 1
					if m[x][y] > longest:
						longest = m[x][y]
						x_longest = x
				else:
					m[x][y] = 0
		return s1[x_longest - longest: x_longest]
	def question(self):
		if self.shortWord1 in self.word1 and self.shortWord2 in self.word2:
			return f'根据{self.word1}和{self.word2}的结果分析，{self.word1}和{self.word2}均为数组类型：\n如果{self.word1}和{self.word2}数量均为1，结束\n如果{self.word1}和{self.word2}任意一个数量不为1,执行步骤{self.steps[0]}'
		commonStr = self.common_substring(self.shortWord1, self.shortWord2)
		return f'检查{self.word1}和{self.word2}数据，{self.word1}和{self.word2}均为数组类型：\n如果{self.word1}和{self.word2}存在{commonStr},结束\n如果{self.word1}和{self.word2}没有{commonStr},执行步骤{self.steps[0]}'

	def answer(self):
		return f'if len({translate.TranslateC(self.shortWord1)})==1 or len({translate.TranslateC(self.shortWord2)})==1: to "stop"\nif len({translate.TranslateC(self.shortWord1)})!=1 and len({translate.TranslateC(self.shortWord2)})!=1: to "{self.steps[0]}"'

class CSingleStatus(CBase):
	
	def custombuilt(self, word):
		super().custombuilt(word)
		self.valRange = self.valRange1
		self.valMean = self.valMean1
		self.mean = ""
		if self.valMean:
			self.mean = "，" + "，".join([f'{self.valRange[i]}表示{self.valMean[i]}' for i in range(len(self.valMean))])
		self.val = random.sample(self.valRange, 1)[0]

	def output(self):
		seriesList = []
		for i in range(2):
			word = getattr(self, f'word{i+1}', "")
			shortWord = getattr(self, f'shortWord{i+1}', "")
			valRange = getattr(self, f'valRange{i+1}')
			valMean = getattr(self, f'valMean{i+1}')
			if not word or not valRange:
				continue
			self.word = word
			self.shortWord = shortWord
			self.valRange = valRange
			self.valMean = valMean
			self.steps = [random.randint(1, 5) for i in range(5)]
			self.mean = ""
			if self.valMean:
				self.mean = "，" + "，".join([f'{self.valRange[i]}表示{self.valMean[i]}' for i in range(len(self.valMean))])
			self.val = random.sample(self.valRange, 1)[0]
			seriesList.append(pd.Series({"问题":self.question(), "答案":self.answer(), "能力":self.modeType}))
		return pd.concat(seriesList, axis=1).transpose()
	def question(self):
		return f'根据{self.word}分析，{self.word}为整数型{self.mean}：\n如果{self.word}为{self.val}，执行步骤"{self.steps[0]}"\n如果{self.word}不为{self.val}，结束'

	def answer(self):
		return f'if {translate.TranslateC(self.shortWord)}=={self.val}: to "{self.steps[0]}"\nf {translate.TranslateC(self.shortWord)}!={self.val}: to "stop"'
	
	

class CDoubleStatus(CBase):
	
	def question(self):
		return super().question()

