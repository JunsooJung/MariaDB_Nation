from flask import Flask, render_template, request
import pymysql
import pandas as pd

host = "localhost"
port = 3306
database = "nation"
username = 'root'
password = '****'
conflag = True

app = Flask(__name__)

db = pymysql.connect(host=host,user=username,password=password,database=database,port=port,charset='utf8')


@app.route('/', methods=['GET', 'POST'])
def index():
    
    db = pymysql.connect(host=host,user=username,password=password,database=database,port=port,charset='utf8')
    cur = db.cursor()

    keyword = request.args.get('keyword', '')  # DB 전체 검색 키워드
    cur.execute("SHOW TABLES")
    tables = [t[0] for t in cur.fetchall()]

    search_results = {}  # DB 전체 검색 결과 저장 {table_name: dataframe}

    if keyword:
        for table in tables:
            # 테이블 데이터 가져오기
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            cur.execute(f"DESCRIBE {table}")
            columns = [c[0] for c in cur.fetchall()]
            df = pd.DataFrame(rows, columns=columns)

            # 모든 컬럼에서 keyword 포함 여부 검색
            mask = df.astype(str).apply(lambda col: col.str.contains(keyword, case=False, na=False))
            df_filtered = df[mask.any(axis=1)]

            if not df_filtered.empty:
                search_results[table] = df_filtered

    db.close()
    return render_template('index.html', tables=tables, search_results=search_results, keyword=keyword)

@app.route('/view_table', methods=['GET', 'POST'])
def view_table():
    
    db = pymysql.connect(host=host,user=username,password=password,database=database,port=port,charset='utf8')
    cur = db.cursor()

    table = request.args.get('table')
    keyword = request.args.get('keyword', '')
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    cur.execute(f"DESCRIBE {table}")
    columns = [c[0] for c in cur.fetchall()]
    db.close()

    df = pd.DataFrame(rows, columns=columns)

    # 테이블 내 검색
    if keyword:
        mask = df.astype(str).apply(lambda col: col.str.contains(keyword, case=False, na=False))
        df = df[mask.any(axis=1)]

    return render_template('view_table.html', df=df.values.tolist(), columns=columns, table=table, keyword=keyword)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

