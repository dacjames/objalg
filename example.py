from abc import ABC, abstractmethod

from objalg import algebra_impl, Union


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


class Pair:
    def A(self):
        self.a.__class__

    def B(self):
        self.b.__class__

    def __init__(self, a, b):
        self.a = a
        self.b = b


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


class VarExpr(Expr):
    def __init__(self, name):
        self.name = name


class Stmt:
    pass


class AssignStmt(Stmt):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class ExprStmt(Stmt):
    def __init__(self, e):
        self.e = e


class BlockStmt(Stmt):
    def __init__(self, *exprs):
        self.exprs = exprs


# ######## #
# ALGEBRAS #
# ######## #

class Algebra(ABC):
    @abstractmethod
    def T(self):
        pass


class IntAlg(Algebra):
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


class StmtAlg(Algebra):
    @abstractmethod
    def var(self, name):
        pass

    @abstractmethod
    def assign(self, name, value):
        pass

    @abstractmethod
    def expr(self, e):
        pass

    @abstractmethod
    def block(self, *exprs):
        pass


# ################# #
# Algebra Instances #
# ################# #

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


class StmtEval(StmtAlg):
    def T(self):
        return Eval

    def __init__(self):
        super().__init__()
        self.variables = {}

    @algebra_impl(VarExpr)
    def var(self, this):
        return self.variables[this.name]

    @algebra_impl(ExprStmt)
    def expr(self, this):
        return this.e.eval()

    @algebra_impl(AssignStmt)
    def assign(self, this):
        self.variables[this.name] = this.value.eval()

    @algebra_impl(BlockStmt)
    def block(self, this):
        if len(this.exprs) == 0:
            return None
        elif len(this.exprs) == 1:
            return this.exprs[0].eval()
        else:
            for i in range(len(this.exprs) - 1):
                this.exprs[i].eval()
            return this.exprs[-1].eval()


class StmtShow(StmtAlg):
    def T(self):
        return Show

    @algebra_impl(VarExpr)
    def var(self, this):
        return this.name

    @algebra_impl(ExprStmt)
    def expr(self, this):
        return this.e.show()

    @algebra_impl(AssignStmt)
    def assign(self, this):
        return "%s = %s" % (this.name, this.value.show())

    @algebra_impl(BlockStmt)
    def block(self, this):
        return "; ".join(e.show() for e in this.exprs)


class Combine(IntAlg):
    def A(self):
        return self.alg1.__class__

    def B(self):
        return self.alg2.__class__

    def T(self):
        class CombinedPair(Pair):
            def A(_):
                return self.A()

            def B(_):
                return self.B()
        return CombinedPair

    def __init__(self, alg1, alg2):
        self.alg1 = alg1
        self.alg2 = alg2

    def literal(self, x):
        return self.T()(self.alg1.literal(x), self.alg2.literal(x))

    def add(self, lhs, rhs):
        return self.T()(
            self.alg1.add(lhs.a, rhs.a),
            self.alg2.add(lhs.b, rhs.b),
        )


class Debug(Combine):
    def __init__(self):
        super().__init__(IntEval(), IntShow())

    def add(self, lhs, rhs):
        print("First expression", lhs.b.show(), "evaluated to", lhs.a.eval())
        print("Second expression", rhs.b.show(), "evaluated to", rhs.a.eval())
        return super().add(lhs, rhs)


def expr(alg):
    return alg.add(alg.literal(1), alg.literal(2))


def expr1(alg):
    return alg.add(alg.literal(1), alg.add(alg.literal(2), alg.literal(2)))


def expr2(alg):
    return alg.iff(alg.boolean(True), alg.literal(10), alg.literal(20))


def expr3(alg):
    return alg.block(
        alg.assign('x', expr(alg)),
        alg.assign('y', alg.literal(3)),
        alg.add(alg.var('x'), alg.var('y')),
    )


def main():
    eval_alg = IntBoolEval()

    stmt_alg = Union(IntBoolEval, StmtEval)()
    show_alg = Union(IntBoolShow, StmtShow)()

    combine_alg = Combine(IntEval(), IntShow())
    debug_alg = Debug()

    alg_expr = expr(eval_alg)

    assert alg_expr.eval() == 3
    assert expr2(eval_alg).eval() == 10
    assert expr3(stmt_alg).eval() == 6

    print(expr1(combine_alg).b.show(), '=>', expr(combine_alg).a.eval())
    print(expr1(debug_alg).b.show(), '=>', expr(debug_alg).a.eval())

    print(expr(show_alg).show(), '=>', expr(stmt_alg).eval())
    print(expr2(show_alg).show(), '=>', expr2(stmt_alg).eval())
    print(expr3(show_alg).show(), '=>', expr3(stmt_alg).eval())


if __name__ == '__main__':
    main()
