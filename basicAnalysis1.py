import streamlit as st
import pandas as pd

# Streamlit 앱 시작
st.title("엑셀 파일 분석 및 테이블 생성 도구")

# 전역 변수
data = None
uploaded_file = None
created_tables = {}

# 파일 업로드 유지
if "data" not in st.session_state:
    st.session_state.data = None
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "created_tables" not in st.session_state:
    st.session_state.created_tables = {}

# 메뉴 선택
menu = st.sidebar.selectbox("메뉴 선택", ["엑셀 업로드", "속성 분석", "테이블 생성", "테이블 다운로드"])

# 엑셀 파일 업로드
if menu == "엑셀 업로드":
    st.header("엑셀 파일 업로드")
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"])

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.data = pd.read_excel(uploaded_file)
        st.success("파일 업로드 성공!")
        st.dataframe(st.session_state.data)

# 속성 분석
elif menu == "속성 분석":
    if st.session_state.data is not None:
        st.header("속성 분석")
        st.write("업로드된 데이터 속성:")
        columns = list(st.session_state.data.columns)
        st.write(columns)

        selected_column = st.selectbox("속성을 선택하세요", columns)

        if selected_column:
            value_counts = st.session_state.data[selected_column].value_counts()
            st.write(f"선택한 속성 '{selected_column}'의 값별 개수:")
            st.dataframe(value_counts)
    else:
        st.warning("먼저 엑셀 파일을 업로드하세요.")

# 테이블 생성
elif menu == "테이블 생성":
    if st.session_state.data is not None:
        st.header("테이블 생성")
        st.write("업로드된 데이터 속성:")
        columns = list(st.session_state.data.columns)
        st.write(columns)

        selected_columns = st.multiselect("조합할 속성을 선택하세요", columns)

        if selected_columns:
            new_table = st.session_state.data[selected_columns]
            table_name = st.text_input("새로운 테이블 이름을 입력하세요")

            if st.button("테이블 생성"):
                if table_name:
                    st.session_state.created_tables[table_name] = new_table
                    st.success(f"테이블 '{table_name}'이 생성되었습니다!")
                    st.dataframe(new_table)
                else:
                    st.error("테이블 이름을 입력하세요.")
    else:
        st.warning("먼저 엑셀 파일을 업로드하세요.")

# 테이블 다운로드
elif menu == "테이블 다운로드":
    if st.session_state.created_tables:
        st.header("테이블 다운로드")
        table_names = list(st.session_state.created_tables.keys())
        selected_table_name = st.selectbox("다운로드할 테이블을 선택하세요", table_names)

        if selected_table_name:
            selected_table = st.session_state.created_tables[selected_table_name]

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
        st.warning("생성된 테이블이 없습니다.")
