

def generate_balance2(sequence, open_to_close):
    r"""
    Iterates through a balanced sequence and reports if the sequence-so-far
    is balanced at that position or not.

    Parameters
    ----------
    sequence: List[Tuple] | str:
        an input balanced sequence

    open_to_close : Dict
        a mapping from opening to closing tokens in the balanced sequence

    Raises
    ------
    UnbalancedException - if the input sequence is not balanced

    Yields
    ------
    Tuple[bool, T, integer]:
        boolean indicating if the sequence is balanced at this index,
        and the current token

    Example
    -------
    >>> open_to_close = {0: 1}
    >>> sequence = [0, 0, 0, 1, 1, 1]
    >>> gen = list(generate_balance2(sequence, open_to_close))
    >>> for flag, token, idx in gen:
    ...     print("flag={:d}, token={}, idx={}".format(flag, token, idx))
    flag=0, token=0
    flag=0, token=0
    flag=0, token=0
    flag=0, token=1
    flag=0, token=1
    flag=1, token=1
    """
    stack = []
    # Traversing the Expression
    for idx, token in enumerate(sequence):

        if token in open_to_close:
            # Push opening elements onto the stack
            stack.append((token, idx))
            prev_idx = None
        else:
            # Check that closing elements
            if not stack:
                raise UnbalancedException
            prev_open, prev_idx = stack.pop()
            want_close = open_to_close[prev_open]

            if token != want_close:
                raise UnbalancedException

        # If the stack is empty the sequence is currently balanced
        currently_balanced = not bool(stack)
        yield currently_balanced, token, prev_idx

    if stack:
        raise UnbalancedException


def reencode_problems(seq1, seq2, index_to_node1, index_to_node2,
                      open_to_close):

    def reencode_seq(seq, open_to_close, offset=0):
        alt_seq = []
        alt_open_to_close = {}
        for idx, info in enumerate(generate_balance2(seq, open_to_close)):
            flag, token, open_idx = info
            alt_tok = chr(idx + offset)
            alt_seq.append(alt_tok)
            if open_idx is not None:
                alt_open_tok = chr(open_idx + offset)
                alt_open_to_close[alt_open_tok] = alt_tok

        alt_seq = ''.join(alt_seq)
        return alt_seq, alt_open_to_close

    alt_seq1, alt_open_to_close1 = reencode_seq(seq1, open_to_close, offset=0)
    offset = ord(alt_seq1[-1]) + 1
    alt_seq2, alt_open_to_close2 = reencode_seq(seq2, open_to_close, offset=offset)

    alt_open_to_close = {}
    alt_open_to_close.update(alt_open_to_close1)
    alt_open_to_close.update(alt_open_to_close2)

    alt_open_to_node = {}
    alt_open_to_node.update(dict(zip(alt_seq1, index_to_node1)))
    alt_open_to_node.update(dict(zip(alt_seq2, index_to_node2)))

    best, value = longest_common_balanced_sequence(
        alt_seq1, alt_seq2, alt_open_to_close,
        open_to_node=alt_open_to_node, node_affinity="auto",
        impl="auto")

    alt_subseq1, alt_subseq2 = best

    # decode to positions
    subidxs1 = [ord(c) for c in alt_subseq1]
    subidxs2 = [ord(c) - offset for c in alt_subseq2]
    return subidxs1, subidxs2


def _lcs_recurse2(
    seq1, idxs1, seq2, idxs2,
    open_to_close, node_affinity,
    index_to_node1, index_to_node2, _memo, _seq_memo1, _seq_memo2,
):
    r"""
    Surprisingly, this recursive implementation is one of the faster
    pure-python methods for certain input types. However, its major drawback is
    that it can raise a RecurssionError if the inputs are too deep.

    Ignore:
        >>> from networkx.algorithms.string.balanced_sequence import _lcs_recurse2  # NOQA
        >>> from networkx.algorithms.string.balanced_sequence import _lcs_recurse  # NOQA

        >>> seq1 = "0010010010111100001011011011"
        >>> seq2 = "001000101101110001000100101110111011"
        >>> open_to_close = {"0": "1"}

        >>> seq1, open_to_close = random_balanced_sequence(10, mode="paren")
        >>> seq2, open_to_close = random_balanced_sequence(10, mode="paren", open_to_close=open_to_close)

        >>> idxs1 = tuple(range(len(seq1)))
        >>> idxs2 = tuple(range(len(seq2)))
        >>> node_affinity = operator.eq
        >>> index_to_node1 = seq1
        >>> index_to_node2 = seq2

        >>> _memo, _seq_memo = {}, {}
        >>> open_to_node = IdentityDict()
        >>> best1, value1 = _lcs_recurse(
        >>>     seq1, seq2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo)
        >>> #
        >>> _memo, _seq_memo1, _seq_memo2 = {}, {}, {}
        >>> best2, value2 = _lcs_recurse2(
        >>>     seq1, idxs1, seq2, idxs2, open_to_close, node_affinity,
        >>>     index_to_node1, index_to_node2, _memo, _seq_memo1, _seq_memo2)

        >>> print("\nseq + idx soln")
        >>> print("value2 = {!r}".format(value2))
        >>> print(best2[0])
        >>> print(best2[2])
        >>> print(best2[1])
        >>> print(best2[3])
        >>> print("".join(list(ub.take(seq1, best2[1]))))
        >>> print("".join(list(ub.take(seq2, best2[3]))))

        >>> #
        >>> print("\nseq only soln")
        >>> print("value1 = {!r}".format(value1))
        >>> print(best1[0])
        >>> print(best1[1])

        import timerit
        ti = timerit.Timerit(1, bestof=1, verbose=3)
        for timer in ti.reset("time"):
            with timer:
                _memo, _seq_memo = {}, {}
                best1, value1 = _lcs_recurse(
                    seq1, seq2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo)


        import timerit
        for timer in ti.reset("time"):
            with timer:
                _memo, _seq_memo1, _seq_memo2 = {}, {}, {}
                best2, value2 = _lcs_recurse2(
                    seq1, idxs1, seq2, idxs2, open_to_close, node_affinity,
                    index_to_node1, index_to_node2, _memo, _seq_memo1, _seq_memo2)

        import xdev
        _memo, _seq_memo1, _seq_memo2 = {}, {}, {}
        _ = xdev.profile_now(_lcs_recurse2)(
            seq1, idxs1, seq2, idxs2, open_to_close, node_affinity,
            index_to_node1, index_to_node2, _memo, _seq_memo1, _seq_memo2)

        _memo, _seq_memo = {}, {}
        best1, value1 = xdev.profile_now(_lcs_recurse)(
            seq1, seq2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo)
    """
    if not seq1:
        return (seq1, idxs1, type(seq1)(), type(idxs1)()), 0
    elif not seq2:
        return (type(seq2)(), type(idxs2)(), seq2, idxs2), 0
    else:
        key1 = idxs1
        key2 = idxs2
        key = (idxs1, idxs2)

        if key in _memo:
            return _memo[key]

        if key1 not in _seq_memo1:
            _seq_memo1[key1] = balanced_decomp_unsafe2(seq1, idxs1, open_to_close)
        decomp1, decomp_idxs1 = _seq_memo1[key1]

        if key2 not in _seq_memo2:
            _seq_memo2[key2] = balanced_decomp_unsafe2(seq2, idxs2, open_to_close)
        decomp2, decomp_idxs2 = _seq_memo2[key2]

        # Case 2: The current edge in sequence1 is deleted
        best, val = _lcs_recurse2(
            decomp1["head_tail"],
            decomp_idxs1["head_tail"],
            seq2,
            idxs2,
            open_to_close,
            node_affinity,
            index_to_node1,
            index_to_node2,
            _memo, _seq_memo1, _seq_memo2,
        )

        # Case 3: The current edge in sequence2 is deleted
        cand, val_alt = _lcs_recurse2(
            seq1,
            idxs1,
            decomp2["head_tail"],
            decomp_idxs2["head_tail"],
            open_to_close,
            node_affinity,
            index_to_node1,
            index_to_node2,
            _memo, _seq_memo1, _seq_memo2,
        )
        if val_alt > val:
            best = cand
            val = val_alt

        # Case 1: The LCS involves this edge
        t1 = index_to_node1[decomp_idxs1["a"][0]]
        t2 = index_to_node2[decomp_idxs2["a"][0]]
        affinity = node_affinity(t1, t2)
        if affinity:
            new_heads, pval_h = _lcs_recurse2(
                decomp1["head"],
                decomp_idxs1["head"],
                decomp2["head"],
                decomp_idxs2["head"],
                open_to_close,
                node_affinity,
                index_to_node1,
                index_to_node2,
                _memo, _seq_memo1, _seq_memo2,
            )
            new_tails, pval_t = _lcs_recurse2(
                decomp1["tail"],
                decomp_idxs1["tail"],
                decomp2["tail"],
                decomp_idxs2["tail"],
                open_to_close,
                node_affinity,
                index_to_node1,
                index_to_node2,
                _memo, _seq_memo1, _seq_memo2,
            )

            new_head1, new_head_idxs1, new_head2, new_head_idxs2 = new_heads
            new_tail1, new_tail_idxs1, new_tail2, new_tail_idxs2 = new_tails

            subseq1 = decomp1["a"] + new_head1 + decomp1["b"] + new_tail1
            subseq2 = decomp2["a"] + new_head2 + decomp2["b"] + new_tail2

            subidxs1 = decomp_idxs1["a"] + new_head_idxs1 + decomp_idxs1["b"] + new_tail_idxs1
            subidxs2 = decomp_idxs2["a"] + new_head_idxs2 + decomp_idxs2["b"] + new_tail_idxs2

            cand = (subseq1, subidxs1, subseq2, subidxs2)
            val_alt = pval_h + pval_t + affinity
            if val_alt > val:
                best = cand
                val = val_alt

        found = (best, val)
        _memo[key] = found
        return found


def balanced_decomp_unsafe2(sequence, indices, open_to_close):
    """
    Similar to :func:`balanced_decomp` but assumes that ``sequence`` is valid
    balanced sequence in order to execute faster.

    Example
    -------
    >>> open_to_close = {0: 1}
    >>> sequence = [0, 0, 0, 1, 1, 1, 0, 1]

    >>> sequence, open_to_close = random_balanced_sequence(3)
    >>> indices = tuple(range(len(sequence)))
    >>> decomp, decomp_idxs = balanced_decomp_unsafe2(sequence, indices, open_to_close)
    >>> decomp1, decomp_idxs1 = balanced_decomp_unsafe2(decomp["head_tail"], decomp_idxs["head_tail"], open_to_close)
    >>> decomp2, decomp_idxs2 = balanced_decomp_unsafe2(decomp1["head_tail"], decomp_idxs1["head_tail"], open_to_close)
    >>> print("decomp = {}".format(ub.repr2(decomp, nl=1)))
    >>> print("decomp1 = {}".format(ub.repr2(decomp1, nl=1)))
    >>> print("decomp2 = {}".format(ub.repr2(decomp2, nl=1)))
    >>> # These commands will error if any decomp is unbalanced
    >>> list(generate_balance(decomp1["head"], open_to_close))
    >>> list(generate_balance(decomp2["head"], open_to_close))
    >>> list(generate_balance(decomp1["tail"], open_to_close))
    >>> list(generate_balance(decomp2["tail"], open_to_close))

    """
    # if indices is None:
    #     indices = tuple(range(len(sequence)))
    gen = generate_balance_unsafe(sequence, open_to_close)

    bal_curr, tok_curr = next(gen)
    want_close = open_to_close[tok_curr]

    head_stop = 1
    for head_stop, (bal_curr, tok_curr) in enumerate(gen, start=1):
        if bal_curr and tok_curr == want_close:
            # do we need the second part of this condition?
            break
    slices = {
        "a": slice(0, 1),
        "b": slice(head_stop, head_stop + 1),
        "head": slice(1, head_stop),
        "tail": slice(head_stop + 1, None),
    }
    decomp_idxs = {key: indices[val] for key, val in slices.items()}
    decomp = {key: sequence[val] for key, val in slices.items()}

    decomp["head_tail"] = decomp["head"] + decomp["tail"]
    decomp_idxs["head_tail"] = decomp_idxs["head"] + decomp_idxs["tail"]
    return decomp, decomp_idxs
