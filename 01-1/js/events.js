/**
 * 폼 유효성 검사 및 사용자 인터랙션 모듈
 * 단일 책임: 실시간 정규식 폼 검증, 에러/성공 피드백 DOM 제어, submit 이벤트 캡슐화
 */

const VALIDATION_RULES = {
  name: {
    validate: (val) => val.trim().length >= 2,
    message: '성함은 최소 2글자 이상 입력해주세요.'
  },
  email: {
    validate: (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim()),
    message: '올바른 이메일 주소 형식(example@domain.com)을 입력해주세요.'
  },
  message: {
    validate: (val) => val.trim().length >= 10,
    message: '메시지는 최소 10글자 이상 구체적으로 작성해주세요.'
  }
};

/**
 * 특정 필드의 유효성을 검사하고 UI를 업데이트하는 함수
 * @param {HTMLFormElement} form - 부모 폼 요소
 * @param {string} fieldName - 필드 이름 ('name', 'email', 'message')
 * @returns {boolean} - 유효 여부
 */
export function validateField(form, fieldName) {
  if (!form || !VALIDATION_RULES[fieldName]) return true;

  const input = form.querySelector(`[name="${fieldName}"]`);
  const errorBox = form.querySelector(`#error-${fieldName}`);
  if (!input || !errorBox) return true;

  const isValid = VALIDATION_RULES[fieldName].validate(input.value);

  if (isValid) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    errorBox.textContent = '';
    errorBox.classList.remove('show');
  } else {
    input.classList.remove('is-valid');
    input.classList.add('is-invalid');
    errorBox.textContent = VALIDATION_RULES[fieldName].message;
    errorBox.classList.add('show');
  }

  return isValid;
}

/**
 * Contact 폼 실시간 검증 및 submit 이벤트 초기화 함수
 * @param {HTMLFormElement} form - 폼 요소
 */
export function initContactForm(form) {
  if (!form) return;

  const fields = ['name', 'email', 'message'];

  // 1. 실시간 입력(input) 및 포커스 이탈(blur) 이벤트 바인딩
  fields.forEach(field => {
    const input = form.querySelector(`[name="${field}"]`);
    if (input) {
      input.addEventListener('input', () => validateField(form, field));
      input.addEventListener('blur', () => {
        // 공백이 아닐 때만 blur 시 검증 피드백 출력
        if (input.value.trim().length > 0) {
          validateField(form, field);
        }
      });
    }
  });

  // 2. 폼 제출(submit) 이벤트 바인딩
  form.addEventListener('submit', (event) => {
    // [중요] 브라우저 기본 새로고침 및 폼 전송 동작 차단
    event.preventDefault();

    let isFormValid = true;

    // 모든 필드 동시 전수 검증
    fields.forEach(field => {
      const valid = validateField(form, field);
      if (!valid) {
        isFormValid = false;
      }
    });

    // 하나라도 실패한 경우 첫 번째 에러 필드로 포커스 이동
    if (!isFormValid) {
      const firstInvalidInput = form.querySelector('.is-invalid');
      if (firstInvalidInput) {
        firstInvalidInput.focus();
      }
      return;
    }

    // 3. 검증 통과 시 성공 UI 렌더링
    const successBox = form.querySelector('#form-success-msg');
    if (successBox) {
      successBox.innerHTML = `
        <i class="fa-solid fa-circle-check success-icon"></i>
        메시지가 성공적으로 전송되었습니다! 기재해주신 이메일로 24시간 내에 회신드리겠습니다.
      `;
      successBox.classList.add('show');

      // 입력창 초기화 및 유효 스타일 제거
      form.reset();
      fields.forEach(field => {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
          input.classList.remove('is-valid');
          input.classList.remove('is-invalid');
        }
      });

      // 6초 후 성공 안내문 부드럽게 닫기
      setTimeout(() => {
        successBox.classList.remove('show');
      }, 6000);
    }
  });
}
