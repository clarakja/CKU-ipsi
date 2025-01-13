import pandas as pd
from google.colab import files

uploaded = files.upload()

# 업로드된 파일 이름 가져오기
file_name = list(uploaded.keys())[0]

# 엑셀 파일을 읽어 첫 번째 행을 컬럼 이름으로 사용하는 데이터프레임 생성
data = pd.read_excel(file_name, header=0)

# 고등학교 별 지원자수 구하기 결과를 새로운 데이터프레임에 저장
value_counts = data["고등학교명"].value_counts()
result_df1 = pd.DataFrame({'고등학교명': value_counts.index, '지원자수': value_counts.values})

# 학교별로 등록하고 환불하지 않은 지원자 수
condition_1 = data["1차등록"] != 1
condition_2 = data["환불"] == 0

# 조건을 모두 만족하는 데이터 필터링
filtered_data = data[condition_1 & condition_2]

# 필터링된 데이터에서 특정 컬럼의 값별 갯수 구하기, 결과를 새로운 데이터 프레임에 저장
column_name = "고등학교명"  # 분석할 컬럼 이름
value_counts = filtered_data[column_name].value_counts()
result_df2 = pd.DataFrame({'고등학교명': value_counts.index, '등록자수': value_counts.values})

# 지원자와 등록자 테이블 합병  공백은 0으로 채우기, 지원자수와 등록자 수를 정수형으로 변환, 등록자 순으로 내림차순 정렬
merged_df = pd.merge(result_df1, result_df2, on='고등학교명', how='outer')
merged_df.fillna(0, inplace=True)
merged_df['지원자수'] = merged_df['지원자수'].astype(int)
merged_df['등록자수'] = merged_df['등록자수'].astype(int)
merged_df_sorted = merged_df.sort_values(by='등록자수', ascending=False)

# 소재지 별 지원자 수 구하고 데이터프레임에 저장
value_counts = data["소재지"].value_counts()
regional_df1 = pd.DataFrame({'소재지': value_counts.index, '지원자수': value_counts.values})

# 소재지별로 등록하고 환불하지 않은 지원자 수 기준으로 필터링
condition_1 = data["1차등록"] != 1
condition_2 = data["환불"] == 0
filtered_data = data[condition_1 & condition_2]

# 필터링된 데이터에서 특정 컬럼의 값별 갯수 구하고 데이터 프레임에 저장
column_name = "소재지"  # 분석할 컬럼 이름
value_counts = filtered_data[column_name].value_counts()
regional_df2 = pd.DataFrame({'소재지': value_counts.index, '등록자수': value_counts.values})

# 지역별로 지원자와 등록자 테이블 합병하고 공백은 0으로 채우기, 지원자수와 등록자 수를 정수형으로 변환, 등록자 순으로 내림차순 정렬
merged_df2 = pd.merge(regional_df1, regional_df2, on='소재지', how='outer')
merged_df2.fillna(0, inplace=True)
merged_df2['지원자수'] = merged_df2['지원자수'].astype(int)
merged_df2['등록자수'] = merged_df2['등록자수'].astype(int)
merged_df_sorted2 = merged_df2.sort_values(by='등록자수', ascending=False)

# 사용자로부터 검색 조건 입력 받기
search_condition = int(input("검색 조건 (등록자 수)을 입력하세요: "))

# 등록자 수가 검색 조건보다 큰 학교만 필터링
filtered_df = merged_df_sorted[merged_df_sorted['등록자수'] > search_condition]

# filtered_df에 고등학교에 해당하는 소재지를 추가

# 원천 데이터로 부터 고등학교에 해당하는 소재지 추출
high_school_locations = data.set_index('고등학교명')['소재지'].to_dict()

# 소재지 항목 추가
filtered_df['소재지'] = filtered_df['고등학교명'].map(high_school_locations)

# 데이터 프레임을 엑셀로 저장
with pd.ExcelWriter('output.xlsx') as writer:
    merged_df_sorted.to_excel(writer, sheet_name='고등학교별 등록 현황', index=False)
    merged_df_sorted2.to_excel(writer, sheet_name='지역별 등록 현황', index=False)
    filtered_df.to_excel(writer, sheet_name='검색 결과', index=False)

# Download the Excel file
files.download('output.xlsx')
