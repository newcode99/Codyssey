-- =====================================================
-- 과제 5-1 | 카페 주문 데이터베이스
-- 파일: 03_queries.sql — 핵심 쿼리 15개
-- =====================================================
-- 카테고리별 구성:
-- [기본 조회]  Q01 ~ Q04 (4개)
-- [JOIN]       Q05 ~ Q08 (4개)
-- [집계]       Q09 ~ Q11 (3개)
-- [서브쿼리]   Q12       (1개)
-- [수정/삭제]  Q13 ~ Q14 (2개)
-- [인덱스]     Q15       (1개)
-- =====================================================

PRAGMA foreign_keys = ON;


-- ═══════════════════════════════════════════════════
-- 【기본 조회】 Q01 ~ Q04
-- ═══════════════════════════════════════════════════

-- Q01: 현재 판매 중인 메뉴 전체 조회 (가격 오름차순 정렬)
-- 확인 목적: WHERE로 조건 필터링 + ORDER BY로 정렬하는 기본 SELECT 패턴
SELECT
    m.id,
    c.name AS 카테고리,
    m.name AS 메뉴명,
    m.price AS 가격
FROM menu m
JOIN category c ON m.category_id = c.id
WHERE m.is_available = 1
ORDER BY m.price ASC;


-- Q02: 가장 최근에 가입한 고객 5명 조회
-- 확인 목적: ORDER BY DESC(내림차순) + LIMIT으로 상위 N개만 가져오는 패턴
SELECT
    id,
    name AS 이름,
    email AS 이메일,
    joined_at AS 가입일
FROM customer
ORDER BY joined_at DESC
LIMIT 5;


-- Q03: 2025년 3월 이후에 발생한 주문 조회
-- 확인 목적: DATE 조건 필터링 (범위 조회)
SELECT
    id AS 주문번호,
    customer_id AS 고객번호,
    ordered_at AS 주문일시,
    status AS 상태
FROM orders
WHERE ordered_at >= '2025-03-01'
ORDER BY ordered_at ASC;


-- Q04: 완료되지 않은 주문(취소 or 처리 중) 조회
-- 확인 목적: 여러 조건을 IN으로 묶어서 필터링하는 패턴
SELECT
    id AS 주문번호,
    customer_id AS 고객번호,
    ordered_at AS 주문일시,
    status AS 상태
FROM orders
WHERE status IN ('cancelled', 'pending')
ORDER BY ordered_at DESC;


-- ═══════════════════════════════════════════════════
-- 【JOIN 조회】 Q05 ~ Q08
-- ═══════════════════════════════════════════════════

-- Q05: [INNER JOIN] 주문 내역에 고객 이름 + 메뉴명 함께 조회
-- 확인 목적: 3개 테이블을 연결해서 "사람이 읽을 수 있는" 결과로 만드는 핵심 패턴
-- ★ INNER JOIN = 양쪽 테이블에 모두 존재하는 데이터만 결과에 포함
SELECT
    o.id AS 주문번호,
    c.name AS 고객명,
    m.name AS 메뉴명,
    od.quantity AS 수량,
    od.unit_price AS 단가,
    (od.quantity * od.unit_price) AS 소계,
    o.ordered_at AS 주문일시
FROM order_detail od
INNER JOIN orders  o ON od.order_id = o.id
INNER JOIN customer c ON o.customer_id = c.id
INNER JOIN menu    m ON od.menu_id = m.id
ORDER BY o.id, m.name;


-- Q06: [INNER JOIN] 주문별 총 결제 금액 계산
-- 확인 목적: JOIN + 집계함수를 결합해 주문 1건의 총액을 구하는 패턴
SELECT
    o.id AS 주문번호,
    c.name AS 고객명,
    o.ordered_at AS 주문일시,
    o.status AS 상태,
    SUM(od.quantity * od.unit_price) AS 총결제금액
FROM orders o
INNER JOIN customer c ON o.customer_id = c.id
INNER JOIN order_detail od ON o.id = od.order_id
GROUP BY o.id, c.name, o.ordered_at, o.status
ORDER BY o.id;


-- Q07: [LEFT JOIN] 주문 기록이 없는 고객까지 포함해서 전체 조회
-- 확인 목적: LEFT JOIN = 왼쪽(customer) 테이블은 전부 출력, 오른쪽(orders)이 없으면 NULL
-- ★ INNER JOIN으로 하면 주문한 고객만 나오고, 주문 안 한 고객은 사라짐
SELECT
    c.id AS 고객번호,
    c.name AS 고객명,
    c.email AS 이메일,
    COUNT(o.id) AS 총주문횟수
FROM customer c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name, c.email
ORDER BY 총주문횟수 DESC;


-- Q08: [LEFT JOIN] 한 번도 주문하지 않은 고객만 조회
-- 확인 목적: LEFT JOIN 후 NULL 조건으로 "관계 없는 데이터"를 찾는 패턴
SELECT
    c.id AS 고객번호,
    c.name AS 고객명,
    c.email AS 이메일,
    c.joined_at AS 가입일
FROM customer c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL;


-- ═══════════════════════════════════════════════════
-- 【집계】 Q09 ~ Q11
-- ═══════════════════════════════════════════════════

-- Q09: 카테고리별 메뉴 수 + 평균 가격 집계
-- 확인 목적: GROUP BY로 그룹을 나누고 COUNT/AVG 집계함수를 사용하는 패턴
SELECT
    c.name AS 카테고리,
    COUNT(m.id) AS 메뉴수,
    AVG(m.price) AS 평균가격,
    MIN(m.price) AS 최저가격,
    MAX(m.price) AS 최고가격
FROM category c
INNER JOIN menu m ON c.id = m.category_id
GROUP BY c.id, c.name
ORDER BY 평균가격 DESC;


-- Q10: 가장 많이 팔린 메뉴 TOP 5 (판매량 기준)
-- 확인 목적: GROUP BY + SUM + ORDER BY + LIMIT 조합으로 "랭킹" 쿼리 만들기
SELECT
    m.name AS 메뉴명,
    c.name AS 카테고리,
    SUM(od.quantity) AS 총판매수량,
    SUM(od.quantity * od.unit_price) AS 총매출액
FROM order_detail od
INNER JOIN menu m ON od.menu_id = m.id
INNER JOIN category c ON m.category_id = c.id
GROUP BY m.id, m.name, c.name
ORDER BY 총판매수량 DESC
LIMIT 5;


-- Q11: 월별 주문 건수 + 매출 집계
-- 확인 목적: 날짜를 연-월로 잘라서 GROUP BY하는 시계열 집계 패턴
-- SQLite 전용 함수: STRFTIME('%Y-%m', 날짜컬럼)으로 '2025-01' 형태로 자름
SELECT
    STRFTIME('%Y-%m', o.ordered_at) AS 연월,
    COUNT(DISTINCT o.id) AS 주문건수,
    SUM(od.quantity * od.unit_price) AS 월매출액
FROM orders o
INNER JOIN order_detail od ON o.id = od.order_id
WHERE o.status = 'completed'
GROUP BY STRFTIME('%Y-%m', o.ordered_at)
ORDER BY 연월 ASC;


-- ═══════════════════════════════════════════════════
-- 【서브쿼리】 Q12
-- ═══════════════════════════════════════════════════

-- Q12: 평균 주문 금액보다 많이 쓴 고객 조회
-- 확인 목적: 서브쿼리(안쪽 SELECT)로 먼저 기준값을 구하고,
--            바깥 쿼리에서 그 값을 조건으로 사용하는 패턴
SELECT
    c.name AS 고객명,
    c.email AS 이메일,
    SUM(od.quantity * od.unit_price) AS 총지출금액
FROM customer c
INNER JOIN orders o ON c.id = o.customer_id
INNER JOIN order_detail od ON o.id = od.order_id
WHERE o.status = 'completed'
GROUP BY c.id, c.name, c.email
HAVING SUM(od.quantity * od.unit_price) > (
    -- 서브쿼리: 전체 고객의 1인당 평균 총지출 계산
    SELECT AVG(customer_total)
    FROM (
        SELECT SUM(od2.quantity * od2.unit_price) AS customer_total
        FROM orders o2
        INNER JOIN order_detail od2 ON o2.id = od2.order_id
        WHERE o2.status = 'completed'
        GROUP BY o2.customer_id
    )
)
ORDER BY 총지출금액 DESC;


-- ═══════════════════════════════════════════════════
-- 【수정/삭제】 Q13 ~ Q14
-- ═══════════════════════════════════════════════════

-- Q13: [UPDATE] 처리 중(pending) 상태인 주문을 완료(completed)로 변경
-- 확인 목적: WHERE 조건을 반드시 명시해야 한다는 UPDATE 핵심 원칙 체득
-- ★ WHERE 없이 UPDATE 하면 테이블 전체가 변경되는 재앙 발생
UPDATE orders
SET status = 'completed'
WHERE status = 'pending'
  AND ordered_at < DATETIME('now', '-1 hour');  -- 1시간 이상 된 pending만 완료 처리


-- Q13 결과 확인
SELECT id AS 주문번호, status AS 변경후상태, ordered_at FROM orders WHERE id = 12;


-- Q14: [DELETE] 취소된 주문의 상세 데이터 삭제
-- 확인 목적: FK로 연결된 데이터 삭제 시 자식 테이블(order_detail)부터 삭제해야 함
-- ★ orders를 먼저 지우면 FK 제약조건 에러 발생 (무결성 보호)

-- Step 1: 취소된 주문의 상세 내역 먼저 삭제 (자식 테이블)
DELETE FROM order_detail
WHERE order_id IN (
    SELECT id FROM orders WHERE status = 'cancelled'
);

-- Step 2: 취소된 주문 자체 삭제 (부모 테이블)
DELETE FROM orders
WHERE status = 'cancelled';

-- Q14 결과 확인: 취소 주문이 사라졌는지 확인
SELECT COUNT(*) AS 남은취소주문수 FROM orders WHERE status = 'cancelled';


-- ═══════════════════════════════════════════════════
-- 【인덱스 확인】 Q15
-- ═══════════════════════════════════════════════════

-- Q15: 생성된 인덱스 목록 확인 + 인덱스 활용 쿼리
-- 확인 목적: 인덱스가 실제로 생성됐는지 확인하고, 인덱스가 걸린 컬럼을 조건으로 사용

-- 현재 DB에 존재하는 인덱스 전체 목록 조회
SELECT
    name AS 인덱스명,
    tbl_name AS 적용테이블
FROM sqlite_master
WHERE type = 'index'
  AND name LIKE 'idx_%'
ORDER BY tbl_name;

-- 인덱스 활용 예시: customer_id(인덱스 적용 컬럼)로 특정 고객의 주문 이력 빠르게 조회
-- 이 쿼리는 idx_orders_customer_id 인덱스를 사용해 Full Scan 없이 빠르게 검색됨
SELECT
    o.id AS 주문번호,
    o.ordered_at AS 주문일시,
    o.status AS 상태,
    SUM(od.quantity * od.unit_price) AS 결제금액
FROM orders o
INNER JOIN order_detail od ON o.id = od.order_id
WHERE o.customer_id = 1   -- ← 이 조건에서 idx_orders_customer_id 인덱스 활용
GROUP BY o.id, o.ordered_at, o.status
ORDER BY o.ordered_at DESC;
