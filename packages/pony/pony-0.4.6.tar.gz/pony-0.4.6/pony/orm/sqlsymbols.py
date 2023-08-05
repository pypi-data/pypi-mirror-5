symbols = [ 'SELECT', 'INSERT', 'UPDATE', 'DELETE',
            'FROM', 'INNER_JOIN', 'LEFT_JOIN', 'WHERE', 'GROUP_BY', 'HAVING',
            'UNION', 'INTERSECT', 'EXCEPT',
            'ORDER_BY', 'LIMIT', 'ASC', 'DESC',
            'DISTINCT', 'ALL', 'AGGREGATES', 'AS',
            'COUNT', 'SUM', 'MIN', 'MAX', 'AVG',
            'TABLE', 'COLUMN', 'PARAM', 'VALUE', 'AND', 'OR', 'NOT',
            'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'IS_NULL', 'IS_NOT_NULL',
            'LIKE', 'NOT_LIKE', 'BETWEEN', 'NOT_BETWEEN',
            'IN', 'NOT_IN', 'EXISTS', 'NOT_EXISTS', 'ROW',
            'ADD', 'SUB', 'MUL', 'DIV', 'POW', 'NEG', 'ABS',
            'UPPER', 'LOWER', 'CONCAT', 'STRIN', 'LIKE', 'SUBSTR', 'LENGTH', 'TRIM', 'LTRIM', 'RTRIM',
            'CASE', 'COALESCE',
            'TO_INT',
            'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND', 'TODAY', 'NOW' ]

globals().update((s, s) for s in symbols)
