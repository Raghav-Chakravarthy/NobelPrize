### Cleaning nobel scraper data
import pandas as pd
import numpy as np
import re
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

nobel_data = pd.read_json('nobel_data.json')
nobel_data['is_winner'] = nobel_data['prize_status'].notnull()
nobel_data.loc[(nobel_data['Gender'] != 'M') & (nobel_data['Gender'] != 'F'), 'Gender'] = 'M'

## Can make separate dataframes for nominees and nominators
nominators = nobel_data[nobel_data['role'] == "Nominator"]
nominees = nobel_data[nobel_data['role'] == "Nominee"]

## calculate number of winners among nominees
unique_nominees = nominees.drop_duplicates(subset=['Name'])
num_winners = unique_nominees['is_winner'].sum()
print("Number of winners: ",num_winners)
print("Winning %: ",(num_winners/len(unique_nominees.index)) *100)

#Group by url to get descriptive statistics at nomination level

print(nominees)
print(nominators)


##Descriptive plots

#Gender: make a bar graph of the proportion of nominees/nominators of each gender. Then make plots for each subgroup and make line graphs showing change over time
#quick data cleaning for gender columns in each df

print(unique_nominees['Gender'].unique()) # What does < mean?
print(unique_nominees[unique_nominees['Gender'] == '<']) # This singular observation appears to be a typo or a misprint. According to all resources I have seen Skraup is male. Therefore we can safely change his gender
# unique_nominees.loc[unique_nominees['Gender'] != '<', 'Gender'] = 'M'


fig, ax = plt.subplots(1,1)
unique_nominees['Gender'].value_counts(normalize = True).round(4).plot(kind = 'bar', ax=ax)

for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))

ax.set_title("Gender Proportions of Nobel Prize Nominees")
ax.set_xlabel("Gender")
ax.set_ylabel("Percentage of Total Nominees")
ax.yaxis.set_major_formatter(PercentFormatter(1))

unique_nominators = nominators.drop_duplicates(subset=['Name'])
gender_fields = unique_nominators['Gender'].unique()
print(gender_fields) # in this df we have a few columns with weird values let's examine them and filter them all out

for char in gender_fields:
	if char != 'M' or char != 'F':
		print(char, unique_nominators.loc[unique_nominators['Gender'] == char,:])#Clearly all of these were meant to be M

# unique_nominators.loc[(unique_nominators['Gender'] != 'M') & (unique_nominators['Gender'] != 'F'), 'Gender'] = 'M'

fig, ax = plt.subplots(1,1)
unique_nominators['Gender'].value_counts(normalize = True).round(4).plot(kind = 'bar', ax = ax)
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
ax.set_title("Gender Proportions of Nobel Prize Nominators")
ax.set_xlabel("Gender")
ax.set_ylabel("Percentage of Total Nominators")
ax.yaxis.set_major_formatter(PercentFormatter(1))

## Gender Proportions Over Time
fig, ax = plt.subplots(1,1)
nominees_gender = nominees.groupby('year')['Gender'].value_counts(normalize=True).unstack()
nominees_gender.plot(kind ='line', legend = True, ax=ax)
ax.set_title("Gender Proportions for Nominees Over Time")
ax.set_ylabel("Proportion")
ax.set_xlabel("Year")

fig, ax = plt.subplots(1,1)
nominators_gender = nominators.groupby('year')['Gender'].value_counts(normalize=True).unstack()
nominators_gender.plot(kind ='line', legend = True, ax=ax)
ax.set_title("Gender Proportions for Nominators Over Time")
ax.set_ylabel("Proportion")
ax.set_xlabel("Year")

#stackplots (to do later)

# fig, ax = plt.subplots(1,1)
# plt.stackplot(nominees_gender[x,y1, y2, y3, labels=['A','B','C'])

## Gender Proportions by Category
fig, axes = plt.subplots(1,5, figsize = (35,9))
fig.suptitle("Nominees Gender Percentages By Prize Category")

nominees_grouped = nominees.groupby('category')
# nominees.groupby('category')['Gender'].value_counts(normalize = True).unstack().plot(kind = 'bar', legend = True, ax=ax)
plot_areas = zip(nominees_grouped.groups.keys(), axes.flatten()) # creates list so that I can match plotting axes with group keys when I iterate
def getSubtitle(key):
	if "Peace" in key:
		return "Peace"
	else:
		return key.split(" ")[-1]
for idx, (key, ax) in enumerate(plot_areas):
    group = nominees_grouped.get_group(key)
    subtitle = getSubtitle(key)
    group['Gender'].value_counts(normalize = True).round(4).plot(kind = 'bar', legend = True, ax=ax)
    ax.set_title(subtitle)
    ax.set_xlabel("Gender")
    ax.set_ylabel("Percentage")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    for p in ax.patches:
    	txt = np.round(p.get_height(), decimals=3) * 100
    	ax.annotate(str(txt)+"%", (p.get_x() * 1.005, p.get_height() * 1.005))

fig, axes = plt.subplots(1,5, figsize = (35,9))
fig.suptitle("Nominators Gender Percentages By Prize Category")

nominators_grouped = nominators.groupby('category')
# nominees.groupby('category')['Gender'].value_counts(normalize = True).unstack().plot(kind = 'bar', legend = True, ax=ax)
plot_areas = zip(nominators_grouped.groups.keys(), axes.flatten()) # creates list so that I can match plotting axes with group keys when I iterate

for idx, (key, ax) in enumerate(plot_areas):
    group = nominators_grouped.get_group(key)
    subtitle = getSubtitle(key)
    group['Gender'].value_counts(normalize = True).round(4).plot(kind = 'bar', legend = True, ax=ax)
    ax.set_title(subtitle)
    ax.set_xlabel("Gender")
    ax.set_ylabel("Percentage")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    for p in ax.patches:
    	txt = np.round(p.get_height(), decimals=3) * 100
    	ax.annotate(str(txt)+"%", (p.get_x() * 1.005, p.get_height() * 1.005))




## Is there at least marginally greater representation of women among winners?
winners = unique_nominees[unique_nominees['is_winner'] == True]

fig, ax = plt.subplots(1,1)
winners['Gender'].value_counts(normalize = True).round(4).plot(kind = 'bar', ax=ax)

for p in ax.patches:
    ax.annotate(str(p.get_height()*100)+"%", (p.get_x() * 1.005, p.get_height() * 1.005))

ax.set_title("Gender Proportions of Nobel Prize Winners")
ax.set_xlabel("Gender")
ax.set_ylabel("Percentage of Total Nominees")
ax.yaxis.set_major_formatter(PercentFormatter(1))



## Age Distributions Nominees/Nominators by overall/by category/binned changes in the distributions
print(nominees.describe())
print(nominators.describe())

## Uncomment and debug later
# fig, ax = plt.subplots(1,1)
# nominees_people = nominees[nominees['category'] != "Nomination for Nobel Peace Prize"]
# nominees_people['age'] = lambda x: nominees_people['year'] - nominees_people['Year, Birth'] if nominees_people['Year, Death'].isnull() else nominees_people['Year, Death'] - nominees_people['Year, Birth']
# print(nominees_people['age'])
# sys.exit()
# nominees_people.boxplot(column = ['age'], grid = False) # Why are their some ages over 300 and why are there negative ages

# pd.options.display.max_colwidth = 100
# print(nominees.loc[nominees['age'] > 200,: 'url'])
# sys.exit()

## data summary at nomination level (avg/median nominees,nominators, etc.)

plt.show()