# Course Analysis Contract

Read this reference only for a full course application analysis or a delivery handoff.

## Standalone output

Use only the sections relevant to the request:

1. **本周课程结论**: central question, method, concepts, and practical meaning.
2. **本周明确必交项**: deliverable, explicit content, deadline, format or channel, acceptance or grading rule, source locator, and evidence status. If none, state `未发现课件明确要求的本周提交物`.
3. **建议准备与待确认项**: keep recommendations separate from formal requirements and source conflicts.
4. **Haiwen 映射**: include only when requested and use only the sanitized repository context.
5. **需要团队判断与下一步**: include only decisions that materially change delivery.

For a submission-only question, normally return sections 2, 3, and 5.

## Delivery handoff fields

Return a compact `Delivery Handoff` containing:

- `course_id`, `week_id`, `topic`, and proposed state;
- `source_manifest` with relevant relative path and stable locator only;
- `explicit_requirements` with ID, deliverable, content, deadline, format or channel, acceptance rule, locator, and status;
- `required_evidence` with quantity, freshness if stated, traceability, and ethical limits;
- `confirmed_inputs` already established in current local files or by the user;
- `workbook_updates` and `coursework_pack_sections`;
- whether a link wrapper is explicitly required;
- `missing_inputs`, `conflicts_and_unknowns`, and any research gap;
- at most one optional project artifact recommendation, or `none`.

Use `none`, `not found`, or `待确认` instead of filling gaps. The handoff is not permission to browse, create files, update a workbook, or finalize claims.
