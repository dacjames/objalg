from abc import ABC, abstractmethod

from objalg import algebra_impl


class Expr:
    pass


class Eval(ABC):
    @abstractmethod
    def eval(self):
        pass


class Show(ABC):
    @abstractmethod
    def show(self):
        pass


class LiteralExpr(Expr):
    def __init__(self, x):
        self.x = x


class AddExpr(Expr):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class BooleanExpr(Expr):
    def __init__(self, b):
        if not isinstance(b, bool):
            raise TypeError(b)
        self.b = b


class IfExpr(Expr):
    def __init__(self, pred, if_expr, else_expr):
        if not isinstance(pred, BooleanExpr):
            raise TypeError(pred)

        self.pred = pred
        self.if_expr = if_expr
        self.else_expr = else_expr


class IntAlg(ABC):
    @abstractmethod
    def T(self):
        pass

    @abstractmethod
    def literal(self, x):
        pass

    @abstractmethod
    def add(self, lhs, rhs):
        pass


class IntBoolAlg(IntAlg):
    @abstractmethod
    def boolean(self, b):
        pass

    @abstractmethod
    def iff(self, e1, e2):
        pass


class IntFactory(IntAlg):
    def T(self):
        return Expr

    def literal(self, x):
        return LiteralExpr(x)

    def add(self, lhs, rhs):
        return AddExpr(lhs, rhs)


class IntEval(IntAlg):
    '''Eval with manual instance creation.
    '''
    def T(self):
        return Eval

    def literal(self, x):
        class EvalLiteral(LiteralExpr, Eval):
            def eval(self):
                return self.x

        return EvalLiteral(x)

    def add(self, lhs, rhs):
        class EvalAdd(AddExpr, Eval):
            def eval(self):
                return self.lhs.eval() + self.rhs.eval()

        return EvalAdd(lhs, rhs)


class IntShow(IntAlg):
    '''Show implementation using the decerator to remove boilerplate
    '''
    def T(self):
        return Show

    @algebra_impl(LiteralExpr)
    def literal(self, this):
        return str(this.x)

    @algebra_impl(AddExpr)
    def add(self, this):
        return "%s + %s" % (this.lhs.show(), this.rhs.show())


class IntBoolEval(IntEval):
    @algebra_impl(BooleanExpr)
    def boolean(self, this):
        return bool(this.b)

    @algebra_impl(IfExpr)
    def iff(self, this):
        if this.pred.eval():
            return this.if_expr.eval()
        else:
            return this.else_expr.eval()


class IntBoolShow(IntShow):
    @algebra_impl(BooleanExpr)
    def boolean(self, this):
        return str(this.b)

    @algebra_impl(IfExpr)
    def iff(self, this):
        return "if %s then %s else %s" % \
               (this.pred.show(),
                this.if_expr.show(),
                this.else_expr.show())


def expr(alg):
    return alg.add(alg.literal(1), alg.literal(2))


def expr2(alg):
    return alg.iff(alg.boolean(True), alg.literal(10), alg.literal(20))


def main():
    eval_alg = IntBoolEval()
    show_alg = IntBoolShow()

    alg_expr = expr(eval_alg)

    print(alg_expr.eval())

    assert alg_expr.eval() == 3
    assert expr2(eval_alg).eval() == 10

    print(expr(show_alg).show())
    print(expr2(show_alg).show())


if __name__ == '__main__':
    main()
