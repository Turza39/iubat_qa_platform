import sys

def solve():
    input_data = sys.stdin.read().split()
    if not input_data: return
    t = int(input_data[0])
    pointer = 1
    
    for _ in range(t):
        n = int(input_data[pointer])
        arr = list(map(int, input_data[pointer+1 : pointer+1+2*n]))
        pointer += 2*n + 1
        
        pos = [[] for _ in range(n)]
        for i, v in enumerate(arr):
            pos[v].append(i)
            
        # The sum of indices for a palindrome centered at S/2 is S
        # We track how many consecutive numbers starting from 0 
        # share the same index sum and are nested.
        
        # Possible sum S ranges from 0 to 2*(2n-1)
        # But we only care about the sum S = pos1[0] + pos2[0]
        s = pos[0][0] + pos[0][1]
        
        max_mex = 1
        # Check how far we can go with this specific center
        # For MEX k, all 0...k-1 must have pos1[i] + pos2[i] == s
        # AND they must be "inside" each other.
        
        # Current boundaries for the 0-th element
        l, r = pos[0][0], pos[0][1]
        
        for k in range(1, n):
            p1, p2 = pos[k][0], pos[k][1]
            if p1 + p2 == s:
                # To be a palindrome, the new pair must either 
                # wrap around the current bounds or be inside them.
                # Since we check 0, 1, 2... in order, we just 
                # need them to share the same center.
                max_mex = k + 1
            else:
                break
        
        print(max_mex)

solve()