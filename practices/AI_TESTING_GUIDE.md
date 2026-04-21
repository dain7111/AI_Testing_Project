# AI Testing Guide for QA Team

## Overview

Testing AI-integrated applications differs fundamentally from traditional web app testing. This guide covers methodology, patterns, and automated evaluation strategies.

---

## Part 1: Traditional vs AI Testing

### Traditional Testing
| Aspect | Traditional | AI Testing |
|--------|-------------|------------|
| Output | Deterministic | Non-deterministic |
| Verification | Exact match | Pattern/tendency match |
| Pass/Fail | Binary | Graded (0-1 confidence) |
| Debugging | Code logic | Prompt + Context |
| Test Cases | Input → Exact Output | Input → Expected Pattern |

### Key Differences

```
Traditional Test:
  Input: user_id=123
  Expected: {"name": "John", "age": 25}
  Verification: exact_match(output, expected)

AI Test:
  Input: "từ 공부 nghĩa là gì"
  Expected: Korean word explanation pattern
  Verification: 
    - Contains word "공부"
    - Contains meaning in Vietnamese
    - Contains examples
    - Tone is helpful
    - Confidence: 0.8+
```

---

## Part 2: Common AI Misunderstanding Patterns

### Pattern 1: Context Corruption
**Issue:** AI hallucinates data that persists across turns, causing cascading errors.

**Example from HanjaHero:**
```
Turn 1: AI hallucinates current_notebook_id=1
Turn 2: User: /save → AI uses notebook_id=1 (invalid)
Turn 3: Error → AI confused, asks wrong question
```

**Detection:**
- AI uses data not from user input or previous tool results
- Values like `id=1`, `id=0` often indicate hallucination

**Fix:** Validate data before use, clear corrupted state on error.

---

### Pattern 2: Selection Index vs Real ID
**Issue:** AI confuses display numbers (1, 2, 3) with actual IDs.

**Example:**
```
AI displays: "1. Học giao tiếp (ID=452)"
User selects: "1"
AI uses: notebook_id=1 ❌ (should be 452)
```

**Detection:**
- AI passes single-digit numbers as IDs
- ID doesn't exist in user's actual data

**Fix:** Prompt explicitly: "1 is SELECTION INDEX, look up `[1] ID=XXX` for real ID"

---

### Pattern 3: Pending Action Override Abuse
**Issue:** AI applies pending_action to unrelated messages.

**Example:**
```
Context: pending_action=awaiting_notebook_selection
User: "학교" (Korean word lookup)
AI classifies: SAVE_CURRENT_WORD ❌ (should be WORD_LOOKUP_SINGLE)
```

**Detection:**
- Intent mismatch with user message content
- Korean text classified as save intent

**Fix:** New intent detection rules - Korean text, questions override pending_action.

---

### Pattern 4: Error Recovery Failure
**Issue:** After error, AI misclassifies user's follow-up message.

**Example:**
```
Turn 1: "Xin lỗi, đã có lỗi xảy ra."
Turn 2: User: "sổ hiện tại của tôi?"
AI: SAVE_CURRENT_WORD ❌ (should be NOTEBOOK_MANAGEMENT)
```

**Detection:**
- Last assistant turn contains error indicators
- User asks new question unrelated to error

**Fix:** Check last turn for errors, ignore pending_action on error recovery.

---

### Pattern 5: Tool Call Loop Incomplete
**Issue:** Tool fails but AI doesn't make follow-up calls.

**Example:**
```
Tool: save_to_notebook fails (invalid notebook_id)
AI: Returns empty message ❌
Expected: AI calls get_user_notebooks to help user select
```

**Detection:**
- Empty response_text when tool fails
- No follow-up tool calls to recover

**Fix:** Allow multiple tool call iterations, pass error to AI for recovery.

---

## Part 3: AI Testing Methodology

### 3.1 Test Case Structure

```yaml
test_case:
  id: TC-AI-001
  name: "Save word with invalid notebook_id recovery"
  
  setup:
    session_state:
      current_notebook_id: 1  # Corrupted value
      recent_lookup_words: ["공부"]
    
  input:
    user_message: "/save"
    
  expected_output_pattern:
    - type: tool_call OR text_response
    - if tool_call: 
        - function: get_user_notebooks  # Recovery action
    - if text:
        - contains: "chọn sổ"
        - tone: helpful
        
  evaluation:
    method: ai_evaluated
    criteria:
      - ai_recognized_invalid_id: true
      - ai_called_recovery_tool: true  
      - message_not_empty: true
    min_confidence: 0.7
```

### 3.2 Multi-Turn Testing

Many AI issues only appear across multiple turns:

```yaml
test_flow:
  id: TF-AI-002
  name: "Notebook selection with number mapping"
  
  turns:
    - turn: 1
      input: "/save"
      expected:
        - calls: get_user_notebooks
        - shows_list: true
        
    - turn: 2
      input: "1"
      context_from_turn_1:
        pending_action:
          notebook_options:
            - {id: 452, name: "Học giao tiếp"}
            - {id: 453, name: "topik 2"}
      expected:
        - calls: save_to_notebook
        - notebook_id: 452  # NOT 1!
        
  evaluation:
    method: ai_evaluated
    criteria:
      - correct_id_mapping: true
      - save_successful: true
```

---

## Part 4: AI-Evaluated Testing (Automated)

### 4.1 Concept

Use LLM to evaluate LLM output:

```
User → AI App → Output → Evaluation LLM → Pass/Fail + Score
```

### 4.2 Implementation

```python
async def evaluate_ai_output(
    test_case: dict,
    actual_output: dict,
    evaluator_llm: LLMProvider,
) -> EvaluationResult:
    """
    Use LLM to evaluate if output matches expected pattern.
    """
    eval_prompt = f"""
    # TASK
    Evaluate if the AI output matches the expected pattern.
    
    # EXPECTED PATTERN
    {test_case['expected_output_pattern']}
    
    # ACTUAL OUTPUT
    {json.dumps(actual_output, ensure_ascii=False)}
    
    # EVALUATION CRITERIA
    - Match type (tool_call/text_response)
    - Match function name (if tool_call)
    - Match content pattern (if text)
    - Correct data usage (no hallucination)
    
    Return JSON:
    {{
      "matches_pattern": true/false,
      "confidence": 0.0-1.0,
      "issues": ["list of problems if any"],
      "reasoning": "brief explanation"
    }}
    """
    
    result = await evaluator_llm.generate_json(
        messages=[{"role": "user", "content": eval_prompt}],
        json_schema={
            "type": "object",
            "properties": {
                "matches_pattern": {"type": "boolean"},
                "confidence": {"type": "number"},
                "issues": {"type": "array", "items": {"type": "string"}},
                "reasoning": {"type": "string"},
            },
            "required": ["matches_pattern", "confidence"],
        },
    )
    
    return EvaluationResult(
        passed=result["matches_pattern"] and result["confidence"] >= 0.7,
        confidence=result["confidence"],
        issues=result.get("issues", []),
        reasoning=result.get("reasoning", ""),
    )
```

### 4.3 Test Runner Example

```python
class AITestRunner:
    """Automated AI testing with LLM evaluation."""
    
    def __init__(self, chat_service, evaluator_llm):
        self.chat_service = chat_service
        self.evaluator_llm = evaluator_llm
    
    async def run_test_case(self, test_case: dict) -> TestResult:
        # Setup session state
        session_id = test_case["setup"].get("session_id", "test-session")
        session_state = test_case["setup"].get("session_state", {})
        
        # Execute
        response = await self.chat_service.chat(
            request=ChatRequest(
                message=test_case["input"]["user_message"],
                conversation_id=session_id,
            ),
            current_user=test_user,
        )
        
        # Evaluate with LLM
        eval_result = await evaluate_ai_output(
            test_case=test_case,
            actual_output={
                "message": response.message,
                "content": response.content,
                "function_calls": response.function_calls,
            },
            evaluator_llm=self.evaluator_llm,
        )
        
        return TestResult(
            test_id=test_case["id"],
            passed=eval_result.passed,
            confidence=eval_result.confidence,
            issues=eval_result.issues,
            actual_output=response,
        )
    
    async def run_test_flow(self, test_flow: dict) -> FlowResult:
        """Run multi-turn test."""
        results = []
        session_state = {}
        
        for turn in test_flow["turns"]:
            # Update context from previous turns
            if "context_from_turn" in turn:
                session_state.update(turn["context_from_turn"])
            
            # Execute turn
            result = await self.run_test_case({
                "id": f"{test_flow['id']}-T{turn['turn']}",
                "setup": {"session_state": session_state},
                "input": {"user_message": turn["input"]},
                "expected_output_pattern": turn["expected"],
            })
            
            results.append(result)
            
            # Update session state from actual output
            if result.actual_output.function_calls:
                for fc in result.actual_output.function_calls:
                    if fc.success and fc.data:
                        session_state.update(fc.data)
        
        return FlowResult(
            flow_id=test_flow["id"],
            passed=all(r.passed for r in results),
            turn_results=results,
        )
```

---

## Part 5: Test Case Examples

### TC-AI-001: Context Corruption Recovery

```yaml
id: TC-AI-001
name: "Handle corrupted current_notebook_id"
severity: high

setup:
  session_state:
    current_notebook_id: 1  # Invalid/hallucinated
    recent_lookup_words: ["공부"]

input:
  user_message: "/save"

expected_output_pattern:
  - one_of:
      - calls: get_user_notebooks  # Recovery: fetch valid list
      - error_message_contains: "invalid"  # Or error with guidance
  
evaluation_criteria:
  - ai_does_not_use_id_1_for_save: true
  - provides_recovery_path: true
  - message_not_empty: true

edge_cases:
  - notebook_id_1_exists_for_user: may pass save (validate ownership)
```

---

### TC-AI-002: Selection Index Mapping

```yaml
id: TC-AI-002  
name: "Correct notebook ID from selection number"
severity: critical

setup:
  session_state:
    pending_action:
      action_type: awaiting_notebook_selection
      data:
        notebook_options:
          - {id: 452, name: "Học giao tiếp"}
          - {id: 453, name: "topik 2"}
    recent_lookup_words: ["공부"]

input:
  user_message: "1"

expected_output_pattern:
  calls: save_to_notebook
  notebook_id: 452  # Real ID, NOT 1

evaluation_criteria:
  - notebook_id_is_real_id_not_index: true
  - notebook_id_is_not_1: true  # Explicit check
  - save_attempted: true

ai_evaluation_prompt: |
  Check if notebook_id in function call is:
  - The REAL ID from notebook_options (452, 453, etc.)
  - NOT the selection index (1, 2, 3)
  
  Pass if notebook_id matches one of the real IDs in options.
```

---

### TC-AI-003: New Intent Override

```yaml
id: TC-AI-003
name: "Korean word overrides pending_action"
severity: high

setup:
  session_state:
    pending_action:
      action_type: awaiting_notebook_selection
    current_notebook_id: 452

input:
  user_message: "학교"  # Korean word, unrelated to save

expected_output_pattern:
  intent: WORD_LOOKUP_SINGLE
  response_contains: "학교" OR "meaning" OR "nghĩa"

evaluation_criteria:
  - intent_is_not_save: true
  - response_is_word_lookup: true
  - korean_word_explained: true

anti_pattern:
  - intent: SAVE_CURRENT_WORD  # Wrong!
  - calls: save_to_notebook    # Wrong!
```

---

### TC-AI-004: Error Recovery Intent

```yaml
id: TC-AI-004
name: "Error recovery - classify new intent correctly"
severity: high

setup:
  session_state:
    last_user_intent: SAVE_CURRENT_WORD
    recent_turns:
      - user: "/save"
        assistant: "Xin lỗi, đã có lỗi xảy ra."  # Error message

input:
  user_message: "sổ hiện tại của tôi?"  # Question about notebooks

expected_output_pattern:
  intent: NOTEBOOK_MANAGEMENT  # NOT SAVE_CURRENT_WORD
  one_of:
    - calls: get_user_notebooks
    - text_response_about_notebooks

evaluation_criteria:
  - intent_not_save_current_word: true
  - recognizes_error_context: true
  - responds_to_actual_question: true
```

---

### TC-AI-005: Tool Failure Recovery

```yaml
id: TC-AI-005
name: "Tool failure triggers recovery actions"
severity: critical

setup:
  session_state:
    current_notebook_id: 1  # Invalid

input:
  user_message: "/save"

expected_output_pattern:
  - sequence:
      - step_1:
          calls: save_to_notebook
          success: false  # Expected to fail
      - step_2:
          calls: get_user_notebooks  # Recovery
          OR text_response_guiding_user

evaluation_criteria:
  - ai_makes_recovery_call: true
  - message_not_empty: true
  - user_guided_to_select_notebook: true
```

---

## Part 6: Evaluation Score Guidelines

| Confidence | Status | Action |
|------------|--------|--------|
| 0.9-1.0 | Pass | Perfect match |
| 0.7-0.89 | Pass | Acceptable variation |
| 0.5-0.69 | Warning | Review manually |
| 0.0-0.49 | Fail | Bug report |

### Acceptable Variations

These variations are acceptable (confidence 0.7+):

1. **Different wording** - Same intent, different text
   ```
   Expected: "Đã lưu vào sổ!"
   Actual: "Từ đã được lưu thành công!"
   Result: Pass (same intent)
   ```

2. **Different emoji** - Different emoji choice
   ```
   Expected: "✅ Đã lưu"
   Actual: "🎉 Đã lưu"  
   Result: Pass (emoji variation)
   ```

3. **Additional helpful content** - More helpful than expected
   ```
   Expected: Shows notebook list
   Actual: Shows notebook list + word preview
   Result: Pass (enhanced helpfulness)
   ```

### Unacceptable Variations

These fail even with high confidence:

1. **Wrong ID usage** - Critical data error
   ```
   Expected: notebook_id=452
   Actual: notebook_id=1
   Result: Fail (data corruption)
   ```

2. **Wrong intent classification**
   ```
   Expected: WORD_LOOKUP_SINGLE
   Actual: SAVE_CURRENT_WORD
   Result: Fail (intent mismatch)
   ```

3. **Empty response on error**
   ```
   Expected: Recovery message
   Actual: "" (empty)
   Result: Fail (no user guidance)
   ```

---

## Part 7: Automated Test Suite

### Running Tests

```bash
# Run all AI tests
python tests/ai/test_ai_patterns.py

# Run specific pattern tests  
python tests/ai/test_ai_patterns.py -k "notebook_selection"

# Run with verbose output
python tests/ai/test_ai_patterns.py -v --evaluator=gpt-4o-mini

# Generate report
python tests/ai/test_ai_patterns.py --report=html
```

### Test Report Output

```json
{
  "summary": {
    "total": 15,
    "passed": 12,
    "warnings": 2,
    "failed": 1,
    "avg_confidence": 0.85
  },
  "failed_tests": [
    {
      "id": "TC-AI-002",
      "issue": "Used selection index (1) as notebook_id instead of real ID (452)",
      "confidence": 0.3,
      "recommendation": "Update prompt to explicitly map [N] to ID=XXX"
    }
  ],
  "warnings": [
    {
      "id": "TC-AI-007",
      "issue": "Response tone slightly less helpful than expected",
      "confidence": 0.65
    }
  ]
}
```

---

## Part 8: Best Practices for QA

### 8.1 Writing AI Test Cases

1. **Focus on patterns, not exact outputs**
   - Expected: "contains explanation of word"
   - Not: "exact text match"

2. **Include edge cases**
   - Invalid IDs, empty states, corrupted context
   - Multi-turn flows with state changes

3. **Document anti-patterns**
   - What AI should NOT do
   - Helps evaluator catch regressions

4. **Use realistic session states**
   - Copy from actual production logs
   - Include corruption scenarios

### 8.2 Evaluating Results

1. **Review failed tests manually**
   - AI evaluator may miss nuances
   - Document patterns for future tests

2. **Track confidence trends**
   - Declining trend = prompt regression
   - Improving trend = prompt optimization working

3. **Categorize failures**
   - Prompt issue → Update prompts
   - Handler issue → Update handlers  
   - Context issue → Update session management

### 8.3 Regression Testing

When prompts are updated:

```bash
# Before update
python tests/ai/test_ai_patterns.py --baseline=before.json

# After update  
python tests/ai/test_ai_patterns.py --compare=before.json

# Check for regressions
# - Previously passing tests should still pass
# - Confidence should not drop significantly
```

---

## Appendix A: Common AI Bugs Catalog

| Bug ID | Pattern | Description | Fix |
|--------|---------|-------------|-----|
| AI-001 | Hallucination | AI creates fake IDs | Validate before use |
| AI-002 | Index confusion | Uses 1,2,3 as IDs | Map to real IDs |
| AI-003 | Intent override abuse | Pending action overrides unrelated messages | New intent detection |
| AI-004 | Error recovery fail | Misclassify after error | Check last turn for errors |
| AI-005 | Empty recovery | No follow-up after tool fail | Multi-iteration loop |
| AI-006 | State leak | Previous turn affects unrelated query | Clear state on error |
| AI-007 | Tool result ignored | Doesn't read tool output | Inject tool results to prompt |

---

## Appendix B: Evaluator Prompt Template

```python
EVALUATOR_PROMPT_TEMPLATE = """
# ROLE
You are an AI output evaluator. Determine if the actual output matches the expected pattern.

# EXPECTED PATTERN
{expected_pattern}

# ACTUAL OUTPUT
{actual_output}

# EVALUATION RULES
1. Pattern Match: Does output type/function match?
2. Content Match: Does content contain expected elements?
3. Data Validity: Is data correct (IDs, values)?
4. Anti-Pattern Check: Does output avoid forbidden patterns?

# CRITICAL CHECKS
{critical_checks}

# SCORING
- 0.9+: Perfect match
- 0.7-0.89: Acceptable variation (different wording ok)
- 0.5-0.69: Partial match, needs review
- 0.0-0.49: Significant mismatch

Return JSON:
{
  "matches_pattern": boolean,
  "confidence": number (0.0-1.0),
  "issues": ["list of problems"],
  "reasoning": "explanation",
  "recommendation": "suggested fix if failed"
}
"""
```

---

## Appendix C: Multi-Turn Test Example

```yaml
test_flow:
  id: TF-AI-MULTI-001
  name: "Complete save flow with recovery"
  
  description: |
    Tests full flow:
    1. Corrupted notebook_id triggers error
    2. AI recovers by fetching notebook list
    3. User selects notebook (number mapping)
    4. Save completes with correct ID
  
  turns:
    - turn: 1
      description: "Initial save with corrupted state"
      setup:
        current_notebook_id: 1  # Invalid
        recent_lookup_words: ["공부"]
      input: "/save"
      expected:
        - calls: [save_to_notebook (fail), get_user_notebooks]
        - shows_list: true
      evaluate:
        - recovery_triggered: true
        - message_not_empty: true
        
    - turn: 2
      description: "User selects notebook"
      setup_from_previous: true  # Uses actual output state
      input: "1"
      expected:
        - calls: save_to_notebook
        - notebook_id: 452  # From context [1] ID=452
      evaluate:
        - correct_id_mapping: true
        - save_success: true
        
  flow_evaluation:
    - all_turns_passed: true
    - state_properly_updated: true
    - no_cascading_errors: true
```

---

## Appendix D: Metrics Dashboard

Track these metrics over time:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Pass Rate | 85%+ | < 70% |
| Avg Confidence | 0.85+ | < 0.70 |
| Intent Accuracy | 95%+ | < 85% |
| ID Mapping Accuracy | 100% | < 95% |
| Recovery Rate | 90%+ | < 70% |

---

## Conclusion

AI testing requires:
1. Pattern-based expectations (not exact outputs)
2. AI-powered evaluation for automation
3. Multi-turn flow testing
4. Regression tracking with confidence scores
5. Catalog of common AI bugs

Key insight: **AI is unpredictable, but patterns are predictable.** Test for patterns, not exact values.

---

*Document Version: 1.0*
*Last Updated: 2026-04-15*
*Author: AI Testing Team*