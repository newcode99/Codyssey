-- =====================================================
-- 과제 5-1 | 카페 주문 데이터베이스
-- 주제: 카페 주문 관리 시스템
-- DB: SQLite 3.43.2
-- 파일: 01_schema.sql — 테이블 생성 (DDL)
-- =====================================================
-- 실행 순서가 중요합니다.
-- FK(외래키)가 참조하는 부모 테이블을 반드시 먼저 만들어야 합니다.
-- 순서: category → menu → customer → orders → order_detail
-- =====================================================


-- ★ SQLite에서 FK 제약조건을 활성화하는 명령어
-- SQLite는 기본적으로 FK를 꺼놓기 때문에 반드시 실행해야 합니다.
PRAGMA foreign_keys = ON;


-- ─────────────────────────────────────────
-- [1] category 테이블 (메뉴 카테고리)
-- 역할: 에스프레소, 프라푸치노 같은 메뉴 분류를 저장합니다.
-- 다른 테이블과의 관계: category 1 → N menu
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS category (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,  -- PK: 자동 증가 고유 번호
    name        VARCHAR(50) NOT NULL UNIQUE,        -- 카테고리명 (중복 불가, 반드시 입력)
    description TEXT                                -- 설명 (선택 입력 가능)
);


-- ─────────────────────────────────────────
-- [2] menu 테이블 (판매 메뉴)
-- 역할: 카페에서 파는 음료/음식 목록을 저장합니다.
-- 다른 테이블과의 관계: category 1 → N menu / menu 1 → N order_detail
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS menu (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,                   -- FK: category 테이블 참조
    name        VARCHAR(100) NOT NULL UNIQUE,       -- 메뉴명 (중복 불가)
    price       INTEGER NOT NULL,                   -- 가격 (원 단위)
    is_available INTEGER NOT NULL DEFAULT 1,        -- 판매 여부 (1=판매중, 0=품절) -- SQLite에는 BOOLEAN이 없어 INTEGER로 대체
    FOREIGN KEY (category_id) REFERENCES category(id)
);


-- ─────────────────────────────────────────
-- [3] customer 테이블 (고객)
-- 역할: 카페를 이용하는 고객 정보를 저장합니다.
-- 다른 테이블과의 관계: customer 1 → N orders
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS customer (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR(50)  NOT NULL,               -- 이름 (반드시 입력)
    email      VARCHAR(100) NOT NULL UNIQUE,        -- 이메일 (중복 불가 — UNIQUE 제약조건)
    phone      VARCHAR(20),                         -- 전화번호 (선택 입력)
    joined_at  DATE NOT NULL DEFAULT (DATE('now'))  -- 가입일 (기본값: 오늘 날짜) -- SQLite 전용 날짜 함수
);


-- ─────────────────────────────────────────
-- [4] orders 테이블 (주문)
-- 역할: 고객이 언제 주문했는지 기록합니다. (주문 1건 = 1행)
-- 다른 테이블과의 관계: customer 1 → N orders / orders 1 → N order_detail
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,                   -- FK: customer 테이블 참조
    ordered_at  DATETIME NOT NULL DEFAULT (DATETIME('now')), -- 주문 일시 -- SQLite 전용
    status      VARCHAR(20) NOT NULL DEFAULT 'pending',      -- 주문 상태: pending/completed/cancelled
    FOREIGN KEY (customer_id) REFERENCES customer(id)
);


-- ─────────────────────────────────────────
-- [5] order_detail 테이블 (주문 상세)
-- 역할: 주문 1건 안에 담긴 각 메뉴와 수량을 저장합니다.
-- (예: 주문 #1에 아메리카노 2잔 + 라떼 1잔)
-- 다른 테이블과의 관계: orders 1 → N order_detail / menu 1 → N order_detail
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_detail (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id  INTEGER NOT NULL,                     -- FK: orders 테이블 참조
    menu_id   INTEGER NOT NULL,                     -- FK: menu 테이블 참조
    quantity  INTEGER NOT NULL DEFAULT 1,           -- 수량 (기본 1개)
    unit_price INTEGER NOT NULL,                    -- 주문 당시 가격 (메뉴 가격이 바뀌어도 기록 보존)
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_id)  REFERENCES menu(id)
);


-- ─────────────────────────────────────────
-- [인덱스] 자주 조회하는 컬럼에 인덱스 적용
-- 이유: orders와 order_detail은 데이터가 가장 많이 쌓이는 테이블입니다.
--       customer_id, order_id로 검색하는 쿼리가 가장 빈번하게 발생하므로
--       해당 컬럼에 인덱스를 걸어 조회 속도를 향상시킵니다.
-- ─────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_orders_customer_id    ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_detail_order_id ON order_detail(order_id);
CREATE INDEX IF NOT EXISTS idx_order_detail_menu_id  ON order_detail(menu_id);
