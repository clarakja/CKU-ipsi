import streamlit as st
import pandas as pd

# Streamlit 앱 제목
st.title("고등학교 및 지역별 지원자 분석 도구")

def upload_excel_file():
    """엑셀 파일 업로드 기능"""
    st.markdown("업로드 파일에는 다음 필드가 포함되어야 합니다: **고등학교명, 소재지, 1차등록, 환불**")
    st.markdown("1차등록 필드값: (미등록자, -1)")
    st.markdown("환불 필드 값: (미환불자, 0)")
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"]) 
    required_columns = ["고등학교명", "소재지", "1차등록", "환불"]
    if not all(col in data.columns for col in required_columns):
        st.error("업로드된 파일에 필수 필드가 누락되었습니다: 고등학교명, 소재지, 1차등록, 환불")
        st.stop()    
        
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file, header=0)
        st.success("파일 업로드 성공!")
        st.dataframe(data.head())
        return data
    return None

def analyze_by_category(data, category_column, filter_conditions, column_name="등록자수", include_field=None):
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

    # 추가 필드 병합
    if include_field:
        field_mapping = data.set_index(category_column)[include_field].to_dict()
        merged_df[include_field] = merged_df[category_column].map(field_mapping)

    merged_df_sorted = merged_df.sort_values(by=column_name, ascending=False)
    
    return merged_df_sorted

def display_analysis_results(data, category_name):
    """분석 결과를 화면에 출력."""
    st.write(f"{category_name}별 지원자 및 등록자 현황")
    st.dataframe(data)

def condition_search_by_count(high_school_analysis, data):
    """인원수 기준 조건 검색 기능"""
    search_condition = st.number_input("등록자 수 기준을 입력하세요", min_value=0, step=1, value=0)
    filtered_df = high_school_analysis[high_school_analysis['등록자수'] > search_condition]

    # 고등학교별 소재지 추가
    high_school_locations = data.set_index('고등학교명')['소재지'].to_dict()
    filtered_df['소재지'] = filtered_df['고등학교명'].map(high_school_locations)

    # 검색 결과 출력
    st.write(f"등록자 수 {search_condition}명 초과 고등학교")
    st.dataframe(filtered_df)

    return filtered_df

def condition_search_by_region(high_school_analysis, data):
    """지역 기준 조건 검색 기능"""
    if '소재지' not in high_school_analysis.columns:
        high_school_analysis['소재지'] = high_school_analysis['고등학교명'].map(
            data.set_index('고등학교명')['소재지'].to_dict()
        )

    unique_regions = high_school_analysis['소재지'].dropna().unique()
    selected_region = st.selectbox("검색할 지역을 선택하세요", unique_regions)

    if selected_region:
        filtered_df = high_school_analysis[high_school_analysis['소재지'] == selected_region]
        st.write(f"선택한 지역 '{selected_region}'의 고등학교 현황")
        st.dataframe(filtered_df)
        return filtered_df
    return None

def download_results(high_school_analysis, regional_analysis, filtered_df):
    """엑셀 다운로드 기능"""
    if st.button("엑셀 파일로 저장"):
        with pd.ExcelWriter('output.xlsx') as writer:
            high_school_analysis.to_excel(writer, sheet_name='고등학교별 등록 현황', index=False)
            regional_analysis.to_excel(writer, sheet_name='지역별 등록 현황', index=False)
            if filtered_df is not None:
                filtered_df.to_excel(writer, sheet_name='검색 결과', index=False)

        st.success("분석 결과가 output.xlsx로 저장되었습니다.")
        with open('output.xlsx', 'rb') as file:
            st.download_button(
                label="엑셀 파일 다운로드",
                data=file,
                file_name='output.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# 메뉴 선택
menu = st.sidebar.selectbox("메뉴 선택", ["엑셀 업로드", "고등학교별 분석", "소재지별 분석", "인원수 기준 검색", "지역 기준 검색", "엑셀 다운로드"])

if "data" not in st.session_state:
    st.session_state.data = None
if "high_school_analysis" not in st.session_state:
    st.session_state.high_school_analysis = None
if "regional_analysis" not in st.session_state:
    st.session_state.regional_analysis = None
if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None

if menu == "엑셀 업로드":
    st.session_state.data = upload_excel_file()

elif menu == "고등학교별 분석" and st.session_state.data is not None:
    high_school_conditions = [
        st.session_state.data["1차등록"] != 1,
        st.session_state.data["환불"] == 0
    ]
    st.session_state.high_school_analysis = analyze_by_category(
        st.session_state.data, "고등학교명", high_school_conditions, include_field="소재지"
    )
    display_analysis_results(st.session_state.high_school_analysis, "고등학교")

elif menu == "소재지별 분석" and st.session_state.data is not None:
    regional_conditions = [
        st.session_state.data["1차등록"] != 1,
        st.session_state.data["환불"] == 0
    ]
    st.session_state.regional_analysis = analyze_by_category(
        st.session_state.data, "소재지", regional_conditions
    )
    display_analysis_results(st.session_state.regional_analysis, "소재지")

elif menu == "인원수 기준 검색" and st.session_state.high_school_analysis is not None:
    st.session_state.filtered_df = condition_search_by_count(
        st.session_state.high_school_analysis, st.session_state.data
    )

elif menu == "지역 기준 검색" and st.session_state.high_school_analysis is not None:
    st.session_state.filtered_df = condition_search_by_region(
        st.session_state.high_school_analysis, st.session_state.data
    )

elif menu == "엑셀 다운로드" and st.session_state.high_school_analysis is not None:
    download_results(
        st.session_state.high_school_analysis,
        st.session_state.regional_analysis,
        st.session_state.filtered_df
    )
