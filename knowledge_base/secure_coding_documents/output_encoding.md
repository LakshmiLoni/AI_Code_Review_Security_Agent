# Output Encoding & Context-Aware Data Sanitization

## 1. Purpose of Output Encoding
Output encoding transforms untrusted data before it is rendered or interpreted by a downstream parser (HTML renderer, JavaScript interpreter, CSS parser, URL resolver, XML parser). By converting special control characters into their safe, inert representations, the target interpreter treats the characters as literal display content rather than executable code.

- **CWE Identifier**: CWE-116 (Improper Encoding or Escaping of Output)
- **OWASP Category**: A03:2021 - Injection

## 2. Context-Specific Encoding Requirements
1. **HTML Body Context**: Convert & to &amp;, < to &lt;, > to &gt;, " to &quot;, ' to &#x27;.
2. **HTML Attribute Context**: Strictly quote all attributes and hex-encode alphanumeric characters.
3. **JavaScript Context**: Encode JSON using Unicode escape sequences (e.g. \u003cscript\u003e).
4. **URL Context**: Use percent-encoding (urllib.parse.quote in Python, URLEncoder.encode in Java).

## 3. Code Implementations

### Python Context Encoding
```python
import html
import urllib.parse
import json

def encode_for_html(untrusted: str) -> str:
    return html.escape(untrusted, quote=True)

def encode_for_url(untrusted: str) -> str:
    return urllib.parse.quote(untrusted, safe='')

def serialize_for_script_tag(data: dict) -> str:
    raw_json = json.dumps(data)
    return raw_json.replace('<', '\u003c').replace('>', '\u003e').replace('&', '\u0026')
```

### Java Output Encoding
```java
import org.owasp.encoder.Encode;

public class OutputSanitizer {
    public static String safeForHtml(String input) {
        return Encode.forHtml(input);
    }

    public static String safeForJavaScript(String input) {
        return Encode.forJavaScript(input);
    }

    public static String safeForUri(String input) {
        return Encode.forUriComponent(input);
    }
}
```

## 4. Architectural Guidelines
- Rely on automated template engines that support context-aware encoding.
- Do not mix raw string concatenation with HTML generation.
