"""
sample_code_eval.py: Example code with intentional flaws for testing CodingEvaluator.

Spec: Write a function that takes a list of integers, removes duplicates,
sorts the result in ascending order, and returns the top-k elements.
The function should handle empty lists and invalid inputs gracefully.
"""

# FLAW 1: No docstring on the function
# FLAW 2: No error handling for non-list input
# FLAW 3: No handling for k > len(items)
# FLAW 4: No handling for empty list edge case
# FLAW 5: Inconsistent naming (items vs lst)

def top_k_unique(lst, k):
    unique = list(set(lst))
    unique.sort()
    return unique[:k]


# FLAW 6: This class has no __init__ docstring and uses bare except
class DataProcessor:
    def process(self, data):
        try:
            result = []
            for item in data:
                if item > 0:
                    result.append(item * 2)
            return result
        except:
            return []


# FLAW 7: Deeply nested, hard to read
def find_nested(matrix, target):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            for k in range(len(matrix[i][j]) if isinstance(matrix[i][j], list) else 0):
                for m in range(3):
                    for n in range(3):
                        if matrix[i][j] == target:
                            return (i, j)
    return None


# Example usage (also flawed, no if __name__ == '__main__' guard)
numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
print(top_k_unique(numbers, 3))
