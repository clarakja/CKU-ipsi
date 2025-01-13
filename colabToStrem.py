import streamlit as st
import pandas as pd

# Streamlit 앱 제목
st.title("고등학교 및 지역별 지원자 분석 도구")

def analyze_by_category(data, category_column, filter_conditions, column_name="등록자수"):
    """지정된 카테고리별 지원자와 등록자 수를 분석하는 함수."""
    # 지원자 수 계산
    value_counts = data[category_column].value_counts()
    result_df1 = pd.DataFrame({category_column: value_counts.index, '지원자수': value_counts.values})

    # 등록자 수 계산
    filtered_data = data
    for condition in filter_conditions:
        filtered_data = filtered_data[condition]

    value_counts = filtered_data[category_column].value_counts()
    result_df2 = pd.DataFrame({category_column: value_counts.index, column_name: value_counts.values})

    # 지원자와 등록자 데이터 병합
    merged_df = pd.merge(result_df1, result_df2, on=category_column, how='outer')
    merged_df.fillna(0, inplace=True)
    merged_df['지원자수'] = merged_df['지원자수'].astype(int)
    merged_df[column_name] = merged_df[column_name].astype(int)
    merged_df_sorted = merged_df.sort_values(by=column_name, ascending=False)
    
    return merged_df_sorted

def display_analysis_results(data, category_name):
    """분석 결과를 화면에 출력."""
    st.write(f"{category_name}별 지원자 및 등록자 현황")
    st.dataframe(data)

# 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"])

if uploaded_file is not None:
    # 엑셀 파일 읽기
    data = pd.read_excel(uploaded_file, header=0)
    st.success("파일 업로드 성공!")

    # 데이터 미리보기
    st.subheader("업로드된 데이터")
    st.dataframe(data.head())

    # 고등학교별 분석
    st.subheader("고등학교별 지원자 및 등록자 분석")
    high_school_conditions = [
        data["1차등록"] != 1,
        data["환불"] == 0
    ]
    high_school_analysis = analyze_by_category(data, "고등학교명", high_school_conditions)
    display_analysis_results(high_school_analysis, "고등학교")

    # 소재지별 분석
    st.subheader("소재지별 지원자 및 등록자 분석")
    regional_conditions = [
        data["1차등록"] != 1,
        data["환불"] == 0
    ]
    regional_analysis = analyze_by_category(data, "소재지", regional_conditions)
    display_analysis_results(regional_analysis, "소재지")

    # 검색 조건
    st.subheader("검색 조건 설정")
    search_condition = st.number_input("등록자 수 기준을 입력하세요", min_value=0, step=1, value=0)

    # 검색 조건 적용
    filtered_df = high_school_analysis[high_school_analysis['등록자수'] > search_condition]

    # 고등학교별 소재지 추가
    high_school_locations = data.set_index('고등학교명')['소재지'].to_dict()
    filtered_df['소재지'] = filtered_df['고등학교명'].map(high_school_locations)

    # 검색 결과 출력
    st.write(f"등록자 수 {search_condition}명 초과 고등학교")
    st.dataframe(filtered_df)

    # 결과 저장
    if st.button("엑셀 파일로 저장"):
        with pd.ExcelWriter('output.xlsx') as writer:
            high_school_analysis.to_excel(writer, sheet_name='고등학교별 등록 현황', index=False)
            regional_analysis.to_excel(writer, sheet_name='지역별 등록 현황', index=False)
            filtered_df.to_excel(writer, sheet_name='검색 결과', index=False)

        st.success("분석 결과가 output.xlsx로 저장되었습니다.")
        with open('output.xlsx', 'rb') as file:
            st.download_button(
                label="엑셀 파일 다운로드",
                data=file,
                file_name='output.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
