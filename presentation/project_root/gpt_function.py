import dotenv
import openai
dotenv.load_dotenv()
def summarize_df_with_gpt_model2(df,whole_data, context="PM 수요 예측"):
    """
    DataFrame을 GPT에 전달해 요약 분석 반환
    """
    table = df.describe()
    # table = df_short.to_markdown(index=False)
    client = openai.OpenAI()
    prompt = f'''1. 다음은 {context} 결과 데이터입니다. {whole_data}

                    2. 특정 행정구의 수요 예측 데이터프레임 {table}
                    - 같은 형식이며, 하나의 행정구만 포함합니다.

                    다음 정보를 정리해 주세요:

                    1. **해당 행정구에서 '공급절대부족' 또는 '공급부족'이 발생하는 시간대**를 날짜와 함께 요약하세요.
                    2. **전체 데이터{whole_data}에서 '공급과다' 또는 '공급평균' 상태인 다른 행정구**를 찾아, 1번에서 확인된 시간대에 맞춰 **PM을 확보할 수 있는 후보 행정구 목록**을 추천해 주세요.
                    3. 해당 행정구(예: 강남구)의 수급 불균형 해소를 위한 **재배치 조치**를 행정운영자 입장에서 추천해 주세요.'''
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # 또는 gpt-4o
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"데이터를 확인하세요. {e}"


def summarize_df_with_gpt_model1(df,whole_data, context="공공자전거 수요 예측"):
    """
    DataFrame을 GPT에 전달해 요약 분석 반환
    """
    table = df.describe()
    # table = df_short.to_markdown(index=False)
    client = openai.OpenAI()
    prompt = f'''1. 다음은 {context} 결과 데이터입니다. {whole_data}

                    2. 특정 행정구의 수요 예측 데이터프레임 {table}
                    - 같은 형식이며, 하나의 행정구만 포함합니다.

                    다음 정보를 정리해 주세요:

                    1. 특정 행정구의 대여량이 400이 초과되는 시간대를 확인하고
                    2. 타 행정구에서 같은 시간대 대여량이 250미만일 경우
                    3. 그 행정구에서 재배치를 추천해주세요'''
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # 또는 gpt-4o
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"데이터를 확인하세요. {e}"