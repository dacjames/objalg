trait ExprAlgegra {
    type Expr
}
class Alg

trait Eval {
  def eval: Int
}

trait Show {
  def show: String
}


trait AddAlg extends ExprAlgegra {

  def literal(x: Int): Expr
  def add(x: Expr, y: Expr): Expr
}




trait EvalAdd extends AddAlg {
  type Expr = Eval

  override def literal(x: Int): Expr =
    new Eval {
      def eval = x
    }

  override def add(lhs: Expr, rhs: Expr): Expr =
    new Eval {
      def eval = lhs.eval + rhs.eval
    }
}

trait ShowAdd extends AddAlg {
  type Expr = Show

  def literal(x: Int): Expr =
    new Show {
      def show: String = x.toString
    }

  def add(lhs: Expr, rhs: Expr): Expr =
    new Show {
      def show: String = s"(${lhs.show} + ${rhs.show})"
    }

}



def expr(alg: AddAlg) =
  alg.add(alg.literal(1), alg.literal(2))

expr(new Alg with EvalAdd).eval
expr(new Alg with ShowAdd).show



trait StmtAlg extends ExprAlgegra {
  type Expr

  def assign(name: String, value: Expr): Expr

  def variable(name: String): Expr

  def block(exprs: Iterable[Expr]): Expr
}

trait ShowStmt extends StmtAlg {
  type Expr = Show

  def expr(f: => String) = new Show {
    def show = f
  }

  override def assign(name: String, value: Expr): Expr =
    expr { s"${name} = ${value.show}" }

  override def variable(name: String): Expr =
    new Show {
      def show = s"${name}"
    }

  override def block(exprs: Iterable[Expr]): Expr =
    new Show {
      def show = s"{${exprs.map(_.show).mkString("\n\t", "\n\t", "\n")}}"
    }
}


import scala.collection.mutable

trait EvalStmt extends StmtAlg {
  type Expr = Eval
  val namespace = mutable.HashMap.empty[String, Expr]

  override def assign(name: String, value: Eval) =
    new Eval {
      def eval = { namespace.put(name, value); value.eval }
    }

  override def variable(name: String) =
    new Eval {
      def eval = namespace.get(name).get.eval
    }

  override def block(exprs: Iterable[Expr]) =
    new Eval {
      def eval =
        exprs.reduce { (a, b) => {a.eval; b} }.eval
    }
}

def expr2(alg: StmtAlg with AddAlg) =
    alg.block(List(
      alg.assign("x", alg.add(alg.literal(5), alg.literal(5))),
      alg.add(alg.variable("x"), alg.literal(1))
    ))



expr2(new Alg with ShowAdd with ShowStmt {
  override type Expr = Show
}).show

expr2(new Alg with EvalAdd with EvalStmt {
  override type Expr = Eval
}).eval












