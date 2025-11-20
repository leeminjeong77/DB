import streamlit as st
import pandas as pd
import duckdb
import time

# --------------------------
# 1️⃣ DuckDB 연결
# --------------------------
con = duckdb.connect('madang.duckdb')  # 앱 내 DB 파일

# --------------------------
# 2️⃣ 테이블 생성 (없으면 생성)
# --------------------------
con.execute("""
CREATE TABLE IF NOT EXISTS Customer (
    custid INTEGER PRIMARY KEY,
    name TEXT,
    address TEXT,
    phone TEXT
)
""")
con.execute("""
CREATE TABLE IF NOT EXISTS Book (
    bookid INTEGER PRIMARY KEY,
    bookname TEXT
)
""")
con.execute("""
CREATE TABLE IF NOT EXISTS Orders (
    orderid INTEGER PRIMARY KEY,
    custid INTEGER,
    bookid INTEGER,
    saleprice INTEGER,
    orderdate DATE
)
""")

# --------------------------
# 3️⃣ 초기 데이터 삽입 (없으면)
# --------------------------
# 고객
if con.execute("SELECT COUNT(*) FROM Customer").fetchone()[0] == 0:
    con.execute("INSERT INTO Customer VALUES (1, '이민정', '서울', '010-1111-1111')")
    con.execute("INSERT INTO Customer VALUES (2, '송민서', '부산', '010-2222-2222')")

# 책
if con.execute("SELECT COUNT(*) FROM Book").fetchone()[0] == 0:
    con.execute("INSERT INTO Book VALUES (1, '파이썬 입문')")
    con.execute("INSERT INTO Book VALUES (2, '데이터 분석 기초')")
    con.execute("INSERT INTO Book VALUES (3, '머신러닝 기초')")

# 주문
if con.execute("SELECT COUNT(*) FROM Orders").fetchone()[0] == 0:
    con.execute("INSERT INTO Orders VALUES (1, 1, 1, 15000, '2025-11-01')")
    con.execute("INSERT INTO Orders VALUES (2, 1, 2, 20000, '2025-11-05')")
    con.execute("INSERT INTO Orders VALUES (3, 2, 3, 25000, '2025-11-07')")

# --------------------------
# 4️⃣ Streamlit UI
# --------------------------
tab1, tab2 = st.tabs(["고객조회", "거래 입력"])

# 고객명 입력
name_input = tab1.text_input("고객명")

if len(name_input) > 0:
    # 고객 주문 정보 조회 (주문 없으면 기본값 표시)
    query_sql = f"""
    SELECT c.custid, c.name,
           COALESCE(b.bookname, '주문없음') AS bookname,
           COALESCE(o.orderdate, '') AS orderdate,
           COALESCE(o.saleprice, 0) AS saleprice
    FROM Customer c
    LEFT JOIN Orders o ON c.custid = o.custid
    LEFT JOIN Book b ON o.bookid = b.bookid
    WHERE c.name = '{name_input}'
    ORDER BY o.orderdate ASC
    """
    result = con.execute(query_sql).fetchdf()
    tab1.write(result)

    # custid 가져오기 (주문이 없어도 고객번호 가져오기)
    cust_row = con.execute(f"SELECT custid FROM Customer WHERE name='{name_input}'").fetchone()
    if cust_row is not None:
        custid = cust_row[0]
        tab2.write("고객번호: " + str(custid))
        tab2.write("고객명: " + name_input)

        # 구매 서적 선택
        books = con.execute("SELECT bookid, bookname FROM Book").fetchall()
        select_book = tab2.selectbox("구매 서적:", [f"{b[0]}, {b[1]}" for b in books])

        # 금액 입력
        price = tab2.text_input("금액")

        # 거래 입력
        if tab2.button("거래 입력"):
            if select_book and price:
                try:
                    bookid = int(select_book.split(",")[0])
                    orderid = con.execute("SELECT COALESCE(MAX(orderid),0)+1 FROM Orders").fetchone()[0]
                    dt = time.strftime('%Y-%m-%d', time.localtime())
                    con.execute(
                        f"INSERT INTO Orders VALUES ({orderid},{custid},{bookid},{price},'{dt}')"
                    )
                    tab2.success("거래가 입력되었습니다.")
                except Exception as e:
                    tab2.error(f"거래 입력 중 오류 발생: {e}")
    else:
        tab2.warning("입력한 이름의 고객이 존재하지 않습니다.")
