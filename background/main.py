from celery_app import simple_task, data_collection_task, level_update_task
import time

def main():
    """메인 애플리케이션에서 백그라운드 태스크 실행"""
    
    print("=== 백그라운드 태스크 실행 예제 ===")
    
    # 1. 간단한 태스크 실행
    print("\n1. 간단한 태스크 실행")
    result = simple_task.delay("Hello Celery!")
    print(f"Task ID: {result.id}")
    print(f"Task Status: {result.status}")
    
    # 2. 데이터 수집 태스크 실행
    print("\n2. 데이터 수집 태스크 실행")
    data_result = data_collection_task.delay()
    print(f"Data Task ID: {data_result.id}")
    
    # 3. 결과 확인
    print("\n4. 태스크 결과 확인 (최대 30초 대기)")
    try:
        # 첫 번째 태스크 결과 확인
        result_value = result.get(timeout=30)
        print(f"Simple Task Result: {result_value}")
        
        # 데이터 수집 태스크 결과 확인
        collection_value = data_collection_task.get(timeout=30)
        print(f"Level Task Result: {collection_value}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== 완료 ===")

if __name__ == '__main__':
    main()