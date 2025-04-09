from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog
import psycopg2

# Função para abrir conexão com o banco
def conectar_banco():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Mangabeiras@40",
        host="localhost",
        port="5432"
    )

# Função para determinar a categoria
def obter_categoria():
    if formulario.radioButton.isChecked():
        return 'Informática'
    elif formulario.radioButton_2.isChecked():
        return 'Alimentos'
    elif formulario.radioButton_3.isChecked():
        return 'Eletrônicos'
    return 'Não informado'

# Inserção no banco
def funcao_principal():
    try:
        codigo = int(formulario.lineEdit.text())
        descricao = formulario.lineEdit_2.text()
        preco = float(formulario.lineEdit_3.text())
        categoria = obter_categoria()

        conexao = conectar_banco()
        cursor = conexao.cursor()

        comando_sql = "INSERT INTO produtos (codigo, descricao, preco, categoria) VALUES (%s, %s, %s, %s)"
        cursor.execute(comando_sql, (codigo, descricao, preco, categoria))

        conexao.commit()
        cursor.close()
        conexao.close()

        # Limpa os campos
        formulario.lineEdit.setText("")
        formulario.lineEdit_2.setText("")
        formulario.lineEdit_3.setText("")

        print("Produto inserido com sucesso!")

    except Exception as e:
        print("Erro ao inserir no banco:", e)

# Exibe e atualiza a segunda tela
def chama_segunda_tela():
    segunda_tela.show()
    atualizar_tabela()

# Atualiza a tabela de produtos
def atualizar_tabela():
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("SELECT * FROM produtos")
        produtos = cursor.fetchall()

        segunda_tela.tableWidget.setRowCount(len(produtos))
        segunda_tela.tableWidget.setColumnCount(4)
        segunda_tela.tableWidget.setHorizontalHeaderLabels(["Código", "Descrição", "Preço", "Categoria"])

        for i, produto in enumerate(produtos):
            for j, valor in enumerate(produto):
                segunda_tela.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(valor)))

        cursor.close()
        conexao.close()

    except Exception as e:
        print("Erro ao buscar produtos:", e)

# Função para deletar produto selecionado
def deletar_produto():
    linha_selecionada = segunda_tela.tableWidget.currentRow()
    if linha_selecionada == -1:
        QMessageBox.warning(segunda_tela, "Atenção", "Selecione um produto para deletar.")
        return

    codigo = segunda_tela.tableWidget.item(linha_selecionada, 0).text()
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("DELETE FROM produtos WHERE codigo = %s", (codigo,))
        conexao.commit()

        cursor.close()
        conexao.close()

        QMessageBox.information(segunda_tela, "Sucesso", "Produto deletado com sucesso!")
        atualizar_tabela()

    except Exception as e:
        print("Erro ao deletar produto:", e)

# Função para editar produto selecionado
def editar_produto():
    linha_selecionada = segunda_tela.tableWidget.currentRow()
    if linha_selecionada == -1:
        QMessageBox.warning(segunda_tela, "Atenção", "Selecione um produto para editar.")
        return

    codigo = segunda_tela.tableWidget.item(linha_selecionada, 0).text()
    descricao = segunda_tela.tableWidget.item(linha_selecionada, 1).text()
    preco = segunda_tela.tableWidget.item(linha_selecionada, 2).text()
    categoria = segunda_tela.tableWidget.item(linha_selecionada, 3).text()

    # Pede os novos valores
    novo_descricao, ok1 = QInputDialog.getText(segunda_tela, "Editar Produto", "Nova descrição:", text=descricao)
    if not ok1: return

    novo_preco, ok2 = QInputDialog.getDouble(segunda_tela, "Editar Produto", "Novo preço:", value=float(preco))
    if not ok2: return

    novo_categoria, ok3 = QInputDialog.getText(segunda_tela, "Editar Produto", "Nova categoria:", text=categoria)
    if not ok3: return

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            "UPDATE produtos SET descricao = %s, preco = %s, categoria = %s WHERE codigo = %s",
            (novo_descricao, novo_preco, novo_categoria, codigo)
        )
        conexao.commit()

        cursor.close()
        conexao.close()

        QMessageBox.information(segunda_tela, "Sucesso", "Produto atualizado com sucesso!")
        atualizar_tabela()

    except Exception as e:
        print("Erro ao editar produto:", e)


# Execução da aplicação
app = QtWidgets.QApplication([])
formulario = uic.loadUi("modelo_form.ui")
segunda_tela = uic.loadUi("lista.ui")

# Botões da primeira tela
formulario.buttonBox.clicked.connect(funcao_principal)
formulario.pushButton.clicked.connect(chama_segunda_tela)

# Botões da segunda tela
segunda_tela.pushButton_2.clicked.connect(deletar_produto)  # botão deletar
segunda_tela.pushButton.clicked.connect(editar_produto)     # botão editar

formulario.show()
app.exec_()
