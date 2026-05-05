import re

class SQLSecurityAuditor:
    FORBIDDEN_KEYWORDS = {"DROP", "TRUNCATE", "DELETE", "ALTER", "GRANT", "REVOKE"}

    def validate_query(self, sql: str) -> bool:
        """Returns True if the query is safe, False otherwise."""
        # Check for destructive keywords
        if any(kw in sql.upper() for kw in self.FORBIDDEN_KEYWORDS):
            return False
        
        # Ensure it's a SELECT query
        if not sql.strip().upper().startswith("SELECT"):
            return False
            
        return True