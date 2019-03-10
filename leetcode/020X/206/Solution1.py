# Definition for singly-linked list.
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None


class Solution:
    def reverseList(self, head):
        if head is None:
          return head
        last = None
        while True:
            tmp = head.next
            head.next = last
            last = head
            if tmp is None:
                return head
            head = tmp


if __name__ == "__main__":
    head = ListNode(1)
    tmp = head
    for i in range(2, 5):
        tmp.next = ListNode(i)
        tmp = tmp.next
    tmp = head
    while tmp is not None:
        print(tmp.val, end=' ')
        tmp = tmp.next
    print(' ')
    solution = Solution()
    tmp = solution.reverseList(head)
    while tmp is not None:
        print(tmp.val, end=' ')
        tmp = tmp.next
    print(' ')
