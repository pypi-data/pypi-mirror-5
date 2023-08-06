1.1
---

- Use ``override_offset`` for overriding ``forbidden.jinja2`` template.
- If user is authenticated but is not authrized for some view,
  render ``forbidden`` page with **Log out** link instead of redirect
  to avoid redirect loop

1.0
---

- Initial version.
