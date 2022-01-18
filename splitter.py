def splitter(text, row_len=20):
    lst = text.split()
    now = [[]]
    n = 0
    for el in lst:
        if len(now[-1]) == 0 or len(el) + n <= row_len - len(el) + 1:
            now[-1].append(el)
            n += len(el)
        else:
            n = 0
            now.append([])
            now[-1] = [el]
    now = [" ".join(i) for i in now]
    m = max(now, key=lambda x: len(x))
    index = now.index(m)
    if len(m) % 2 != 1:
        now[index] += " "
    m = len(now[index])
    for i in range(len(now)):
        if i == index:
            continue
        l = len(now[i])
        if l % 2 != 0:
            now[i] += " "
            l += 1
        now[i] = " " * (m - l) + now[i] + " " * (m - l)
    new = "\n".join(now)
    return new
