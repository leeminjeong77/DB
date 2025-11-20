import streamlit as st 
import pymysql
import pandas as pd
dbConn = pymysql.connect(user='root', passwd='1234', host='localhost', db='madang', charset='utf8')
cursor = dbConn.cursor(pymysql.cursors.DictCursor)

name = st.text_input("고객명")
if name is not None:
       sql = "select c.name, b.bookname, o.orderdate, o.saleprice from Customer c, Book b, Orders o \
       where c.custid = o.custid and o.bookid = b.bookid and name = '" + name + "';"
       cursor.execute(sql)
       result = cursor.fetchall()
       result = pd.DataFrame(result)
       st.write(result)

       if len(name) > 0:
              sql = ''' select c.custid, c.name, b.bookname, o.orderdate, o.saleprice from Customer c, Book b, Orders o 
                     where c.custid = o.custid and o.bookid = b.bookid and name = '" + name + "';" '''
              cursor.execute(sql)
              result = cursor.fetchall()
              result = pd.DataFrame(result)
              tab1.write(result)

              if select_book is not None:
                     bookid = select_book.split(",")[0]
                     dt = time.localtime()
                     dt = time.strftime('%Y-%m-%d', dt)
                     print(dt)
                     print(bookid)
                     price = tab2.text_input("금액")
                     sql = "insert into orders (custid, bookid, saleprice, orderdate) \                         values (" + str(custid) + "," + str(bookid) + "," + str(price) + ",'" + dt + "');"
                     if tab2.button('거래 입력'):
                            print(cursor.execute(sql))
                            dbConn.commit()
                            tab2.write('거래가 입력되었습니다.')
