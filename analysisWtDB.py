import streamlit as st
import pandas as pd
import sqlite3

# SQLite 데이터베이스 설정
DB_FILE = "tables.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 테이블 저장을 위한 데이터베이스 초기화
cursor.execute("CREATE TABLE IF NOT EXISTS tables (name TEXT PRIMARY KEY, data TEXT)")
conn.commit()

# Streamlit 앱 시작
st.title("엑셀 파일 분석 및 테이블 생성 도구")

# 전역 변수
uploaded_file = None

def save_table_to_db(table_name, table_data):
    """테이블을 데이터베이스에 저장."""
    table_data_json = table_data.to_json()
    cursor.execute("REPLACE INTO tables (name, data) VALUES (?, ?)", (table_name, table_data_json))
    conn.commit()

def load_table_from_db(table_name):
    """데이터베이스에서 테이블 로드."""
    cursor.execute("SELECT data FROM tables WHERE name = ?", (table_name,))
    result = cursor.fetchone()
    if result:
        return pd.read_json(result[0])
    return None

def get_table_names():
    """데이터베이스에서 테이블 이름 목록 가져오기."""
    cursor.execute("SELECT name FROM tables")
    return [row[0] for row in cursor.fetchall()]

# 메뉴 선택
menu = st.sidebar.selectbox("메뉴 선택", ["엑셀 업로드", "속성 분석", "테이블 생성", "테이블 병합", "테이블 다운로드"])

# 엑셀 파일 업로드
if menu == "엑셀 업로드":
    st.header("엑셀 파일 업로드")
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"])

    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        st.session_state["uploaded_data"] = data
        st.success("파일 업로드 성공!")
        st.dataframe(data)

# 속성 분석
elif menu == "속성 분석":
    if "uploaded_data" in st.session_state:
        data = st.session_state["uploaded_data"]
        st.header("속성 분석")
        st.write("업로드된 데이터 속성:")
        columns = list(data.columns)
        st.write(columns)

        selected_columns = st.multiselect("속성을 선택하세요", columns)

        if selected_columns:
            conditions = {}

            for column in selected_columns:
                st.subheader(f"속성 '{column}' 조건 설정")
                unique_values = data[column].dropna().unique()

                # 조건 유형 선택
                condition_type = st.selectbox(
                    f"'{column}'의 조건을 선택하세요",
                    ["Count", "같다", "같지 않다"]
                )

                if condition_type == "Count":
                    st.write(f"'{column}' 값별 개수:")
                    value_counts = data[column].value_counts()
                    st.dataframe(value_counts)
                elif condition_type == "같다":
                    if data[column].dtype == 'object' or len(unique_values) <= 10:
                        selected_values = st.multiselect(f"'{column}'의 값을 선택하세요", unique_values)
                        if selected_values:
                            conditions[column] = data[column].isin(selected_values)
                    else:
                        selected_value = st.selectbox(f"'{column}'의 값을 선택하세요", unique_values)
                        conditions[column] = data[column] == selected_value
                elif condition_type == "같지 않다":
                    if data[column].dtype == 'object' or len(unique_values) <= 10:
                        unselected_values = st.multiselect(f"'{column}'에서 제외할 값을 선택하세요", unique_values)
                        if unselected_values:
                            conditions[column] = ~data[column].isin(unselected_values)
                    else:
                        unselected_value = st.selectbox(f"'{column}'에서 제외할 값을 선택하세요", unique_values)
                        conditions[column] = data[column] != unselected_value

            if conditions:
                combined_condition = pd.Series([True] * len(data))
                for condition in conditions.values():
                    combined_condition &= condition

                filtered_data = data[combined_condition]
                st.write("조건에 맞는 데이터:")
                st.dataframe(filtered_data)

                save_table = st.checkbox("이 데이터를 새로운 테이블로 저장하시겠습니까?")
                if save_table:
                    table_name = st.text_input("새로운 테이블 이름을 입력하세요")
                    if st.button("테이블 저장"):
                        if table_name:
                            save_table_to_db(table_name, filtered_data)
                            st.success(f"테이블 '{table_name}'이 저장되었습니다!")
                        else:
                            st.error("테이블 이름을 입력하세요.")
    else:
        st.warning("먼저 엑셀 파일을 업로드하세요.")

# 테이블 생성
elif menu == "테이블 생성":
    if "uploaded_data" in st.session_state:
        data = st.session_state["uploaded_data"]
        st.header("테이블 생성")
        st.write("업로드된 데이터 속성:")
        columns = list(data.columns)
        st.write(columns)

        selected_columns = st.multiselect("조합할 속성을 선택하세요", columns)

        if selected_columns:
            new_table = data[selected_columns]
            table_name = st.text_input("새로운 테이블 이름을 입력하세요")

            if st.button("테이블 생성"):
                if table_name:
                    save_table_to_db(table_name, new_table)
                    st.success(f"테이블 '{table_name}'이 생성되었습니다!")
                    st.dataframe(new_table)
                else:
                    st.error("테이블 이름을 입력하세요.")
    else:
        st.warning("먼저 엑셀 파일을 업로드하세요.")

# 테이블 병합
elif menu == "테이블 병합":
    table_names = get_table_names()
    if table_names:
        st.header("테이블 병합")
        selected_tables = st.multiselect("병합할 테이블을 선택하세요", table_names)

        if selected_tables:
            merge_type = st.radio("병합 방법을 선택하세요", ("수평 병합", "수직 병합"))
            table_name = st.text_input("병합된 테이블 이름을 입력하세요")

            if st.button("테이블 병합"):
                if table_name:
                    try:
                        tables_to_merge = [load_table_from_db(table) for table in selected_tables]
                        if merge_type == "수평 병합":
                            merged_table = pd.concat(tables_to_merge, axis=1)
                        elif merge_type == "수직 병합":
                            merged_table = pd.concat(tables_to_merge, axis=0)

                        save_table_to_db(table_name, merged_table)
                        st.success(f"테이블 '{table_name}'이 병합되었습니다!")
                        st.dataframe(merged_table)
                    except Exception as e:
                        st.error(f"병합 중 오류가 발생했습니다: {e}")
                else:
                    st.error("병합된 테이블의 이름을 입력하세요.")
        else:
            st.info("병합할 테이블을 선택하세요.")
    else:
        st.warning("병합할 테이블이 없습니다.")

# 테이블 다운로드
elif menu == "테이블 다운로드":
    table_names = get_table_names()
    if table_names:
        st.header("테이블 다운로드")
        selected_table_name = st.selectbox("다운로드할 테이블을 선택하세요", table_names)

        if selected_table_name:
            selected_table = load_table_from_db(selected_table_name)

            if st.button("엑셀 파일로 다운로드"):
                output_file = f"{selected_table_name}.xlsx"
                selected_table.to_excel(output_file, index=False)

                with open(output_file, "rb") as file:
                    st.download_button(
                        label="엑셀 파일 다운로드",
                        data=file,
                        file_name=output_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    else:
        st.warning("다운로드할 테이블이 없습니다.")
