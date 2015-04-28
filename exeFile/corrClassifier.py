import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('../corr_result/HighCorr/itemsDetail.csv')


plus_df = df[df['Corr']>0]
minus_df = df[df['Corr']<0]

print 'count of positive corr items:', len(plus_df)
print 'count of negative corr items:', len(minus_df)


plus_class = plus_df.groupby(['classname']).size()
minus_class = minus_df.groupby(['classname']).size()

plus_quality = plus_df.groupby(['qualityname']).size()
minus_quality = minus_df.groupby(['qualityname']).size()

plotting_list = [plus_class, plus_quality, minus_class,  minus_quality]

for idx in range(0, len(plotting_list)):
	plt.subplot(2, 2, idx+1)
	plt.title(idx)
	plt.xlim([0,300	])
	plotting_list[idx].plot(kind='barh')

	#plt.draw()
plt.show()
