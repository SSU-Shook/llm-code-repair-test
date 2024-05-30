# 코딩 컨벤션 프로파일

ESLint는 Javascript를 위한 정적 분석 라이브러리로 코드의 퀄리티를 보장한다.

Prettier는 코드의 스타일링에만 집중하는 Formatter의 역할을 한다.

## ESLint_rules

EsLint_rules의 구조는 다음과 같다.

```jsx
curly: ["error", "all" | "multi" | "multi-line" | "multi-or-nest"]

one-var: ["error", "always" | "never" | "consecutive"]

eququq: ["error", "always" | "smart"]

id-match: ["error", "style", "properties" | "classFields" | "onlyDeclarations" | "ignoreDestructuring"]

no-lonely-if: "error"

no-multi-assign: "error"

operator-assignment: ["error", "always" | "never"]
```

### rules_상세설명

- curly : {} 사용
    - all : 전부 사용
    - multi : 블록에 여러 문장이 있는 경우에만 블록 문을 사용하도록 지정하고, 블록에 하나의 문장만 있을 때 경고
    - multi-line : if, else if, else, for, while, 또는 do의 단일 라인 몸체에 대해 중괄호 없이 허용하면서, 다른 경우에는 중괄호 사용을 강제하는 규칙을 완화
    - multi-or-nest : 몸체가 하나의 단일 라인 문장만 포함하는 경우 if, else if, else, for, while, 또는 do에 대해 중괄호 없이 사용을 강제하고, 그 외의 경우에는 모두 중괄호를 사용하도록 강제
    
- one-var : 함수 내에서 변수 선언시 함께? 분리?
    - always : requires one variable declaration per scope
    - never : requires multiple variable declarations per scope
    - consecutive : allows multiple variable declarations per scope but requires consecutive variable declarations to be combined into a single declaration

- eququq : use the type-safe equality operators `===` and `!==` instead of their regular counterparts `==` and `!=`
    - always : enforces the use of === and !== in every situation
        - null을 어떻게 대할지 추가적인 옵션 지정 가능 (always, never, ignore)
    - smart : enforces the use of === and !== except for these cases:
        - Comparing two literal values
        - Evaluating the value of `typeof`
        - Comparing against `null`
    
- id-match : Require identifiers to match a specified regular expression
    - 우선 스타일 지정. 스타일의 예시는 아래와 같고 마음대로 지정 가능 (issue : 스타일 경우의 수가 너무 많음..)
        - `^[a-z]+([A-Z][a-z]+)*$`  ex)myFavoriteColor
        - `^[A-Z][a-z]+([A-Z][a-z]+)*$`  ex)MyFavoriteColor
        - `^[^_]+$` ex)myclass, myClass (밑줄만 없으면 됨!)
        - `^[a-z]+[_]+([a-z]+)*$` ex)my_class
        
    - `"properties": false` (default) does not check object properties
    - `"properties": true` requires object literal properties and member expression assignment properties to match the specified regular expression
    - `"classFields": false` (default) does not check class field names
    - `"classFields": true` requires class field names to match the specified regular expression
    - `"onlyDeclarations": false` (default) requires all variable names to match the specified regular expression
    - `"onlyDeclarations": true` requires only `var`, `const`, `let`, `function`, and `class` declarations to match the specified regular expression
    - `"ignoreDestructuring": false` (default) enforces `id-match` for destructured identifiers
    - `"ignoreDestructuring": true` does not check destructured identifiers

- no-lonely-if : Disallow `if` statements as the only statement in `else` blocks
    - 따로 지정할 옵션 없음

- no-multi-assign : using multiple assignments within a single statement
    - 따로 지정할 옵션 없음
    - 해당 rule과 one-var와 약간 중첩됨..

- operator-assignment : Require or disallow assignment operator shorthand where possible
    - always : (default) requires assignment operator shorthand where possible
    - never : disallows assignment operator shorthand

## Prettier_rules

Prettier_rules의 구조는 다음과 같다.

```jsx
	"arrowParens": "always" | "avoid",
	"bracketSpacing": true | false,
	"bracketSameLine": true | false,
  "jsxSingleQuote": true | false,
  "proseWrap": "always" | "never" | "preserve",
  "quoteProps": "as-needed" | "consistent" | "preserve"
  "semi": true | false,
  "singleQuote": true | false,
  "tabWidth": 2 | 4,
  "trailingComma": "all" | "es5" | "none", 
  "useTabs": true | false,
  "vueIndentScriptAndStyle": true | false,
```

- arrowParens : 화살표 함수의 매개변수가 하나일 때 괄호 유무
    
    ```jsx
    // always
    const add = (a) => a + 5;
    
    // avoid
    const add = a => a + 5;
    ```
    

- bracketSpacing : 객체 리터럴에서 괄호 사이에 공백 유무
    
    ```jsx
    // true
    const obj = { fooo: "bar" };
    
    // false
    const obj = {foo: "bar"};
    ```
    
- bracketSameLine : JSX에서 닫는 괄호 > 위치
    
    ```jsx
    // true
    <App foo = "bar" />
    
    // false
    <App
    	foo = "bar"
    />
    ```
    
- jsxSingleQuote : JSX에서 인용부호 선택
    
    ```jsx
    // true
    const element = <App foo = 'bar'> Hello </App>;
    
    // false
    const element = <App foo = "bar"> Hello </App>l
    ```
    
- proseWrap : markdown파일에서 줄바꿈
    - always : markdown 파일에서 항상 줄바꿈을 적용
    - never : markdown 파일에서 줄바꿈을 하지 않음
    - preserve : markdown 파일에서 원래의 줄바꿈을 유지

- quoteProps : 인용부호 유무
    
    ```jsx
    // as-needed
    const obj = { foo: "bar", "baz-qux": 42 };
    
    // consistent
    const obj = { "foo": "bar", "baz": 42 };
    
    // preserve
    const obj = { "foo": "bar", "baz-qux": 42 };
    ```
    
- semi : 세미콜론 여부
    
    ```jsx
    // true
    const name = "World";
    console.log(`Hello, ${name}`);
    
    // false
    const name = "World"
    console.log(`Hello, ${name}`)
    ```
    
- singleQuote : 인용부호 선택
    
    ```jsx
    // true
    const greeting = 'Hello, world!';
    
    // false
    const greeting = "Hello, world!";
    ```
    
- tabWidth : 탭 너비
    
    ```jsx
    // 2
    const obj = {
      foo: "bar"
    };
    
    // 4
    const obj = {
        foo: "bar"
    };
    ```
    
- trailingComma : 후행 comma 사용 경우
    
    ```jsx
    // all
    const arr = [
      1,
      2,
    ];
    
    // es5
    const arr = [
      1,
      2,
    ];
    
    // none
    const arr = [
      1,
      2
    ];
    ```
    
- useTabs : 탭 / 스페이스 사용
    
    ```jsx
    // true : 탭 사용
    const obj = {
    	foo: "bar"
    };
    
    // false : 스페이스 사용
    const obj = {
      foo: "bar"
    };
    ```
    

- vueIndentScriptAndStyle : Vue 파일의 <script>와 <style> 태그 내용 들여쓰기 유무
    
    ```jsx
    // true
    <script>
      export default {
        name: "App"
      };
    </script>
    
    // false
    <script>
    export default {
      name: "App"
    };
    </script>
    
    ```