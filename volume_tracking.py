import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta, timezone

st.title('Theo dõi khối lượng mua bán chủ động')

#function for get data and clean data
@st.cache
def get_data(symbol):
  #send request to get data
  url='https://svr1.fireant.vn/api/Data/Markets/IntradayQuotes?symbol='+symbol.upper()
  r=requests.get(url)
  df=pd.DataFrame(r.json())
  
  #Choose needed columns
  df=df.iloc[1:,[2,3,4,6]]
  df.columns=['date_time','price','volume','side']
 
  #Convert datetime
  df['date_time']=pd.to_datetime(df['date_time'],utc=True)
  df['date_time'] = df['date_time'].dt.tz_convert('Asia/Ho_Chi_Minh')
  df=df[(df['side']=='B')|(df['side']=='S')]
  
  df_cum = df.groupby(['side','date_time','price']).sum().groupby(level=0).cumsum().reset_index()
  df_cum=df_cum.reset_index()
  df_cum=df_cum.sort_values('date_time',ascending=True).set_index('date_time',drop=True)

  #calculate net volume
  df_cum['buy_vol']=df_cum['volume']
  df_cum['sell_vol']=df_cum['volume']
  df_cum.loc[df_cum['side']=='S','buy_vol']=np.nan
  df_cum.loc[df_cum['side']=='B','sell_vol']=np.nan
  df_cum.ffill(inplace=True)
  df_cum.fillna(value=0,inplace=True)
  df_cum['net_vol']=df_cum['buy_vol']-df_cum['sell_vol']
  df_cum.drop(columns=['index','buy_vol','sell_vol'],inplace=True)

  return df_cum

#function for plotting
def plot_data(df,name):
  fig,ax = plt.subplots()
  fig.set_size_inches(16,8)
  plt.style.use("seaborn-white") #seaborn-white'
  ax.plot(df.index,df.price,color='#4CB4FF', alpha = 0.5)
  ax.legend(labels=['price'],loc=0)
  ax2=ax.twinx()
  ax2.plot(df.index,df.net_vol,color='#EF5350')
  ax2.legend(['net volume (buy-sell)'],loc='lower right')
  ax.set_title('Net volume tích lũy (Buy - Sell) của ' + r'$\bf{' +  name.upper() + '}$',fontsize= 30) 
  #plt.show()


symbol = st.text_input(label='Nhập mã chứng khoán vào ô bên dưới sau đó nhấn Enter', value='vn30f1m')
try:
    data_load_state = st.text('Xin chờ một chút...')
    df=get_data(symbol)
    data_load_state.text('Đã tải xong! Vui lòng xem biểu đồ hoặc nhấn nút bên dưới để xem data thô')
    
    plot_data(df,symbol)
    st.pyplot(plt)
        
    if st.button('Xem data thô'):
        st.subheader('Raw data')
        st.write(df)
except:
    st.write('Đã có lỗi, có thể bạn đã nhập sai mã chứng khoán')