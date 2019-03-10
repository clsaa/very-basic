# Definition for singly-linked list.
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None


class Solution:
    def swapPairs(self, head):
        if head is None or head.next is None:
            return head
        lnode = head
        rnode = head.next
        head = rnode
        last = None
        while True:
            last = lnode
            rtmp = rnode.next
            rnode.next = lnode
            lnode.next = rtmp
            if rtmp is None or rtmp.next is None:
                return head
            lnode = rtmp
            rnode = rtmp.next
            last.next = rnode


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
    tmp = solution.swapPairs(head)
    while tmp is not None:
        print(tmp.val, end=' ')
        tmp = tmp.next
    print(' ')
