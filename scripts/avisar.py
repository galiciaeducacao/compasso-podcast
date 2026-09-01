# -*- coding: utf-8 -*-
"""Avisa o Paulo por e-mail o resultado de cada passo da esteira.

  python scripts/avisar.py <passo> <ok|falhou|pulou> "<detalhe>"

Existe porque durante cinco dias seguidos algum passo falhou e o Paulo so descobriu
pelo silencio, de manha, com o programa fora do ar. Issue no GitHub depende de ele
estar acompanhando o repositorio; e-mail chega.

O aviso sai em TODOS os desfechos, nao so na falha. Saber que o passo das 15h30 deu
certo e o que permite dormir; receber aviso so quando quebra ensina a ignorar caixa
de entrada silenciosa, porque silencio tambem e o que acontece quando o proprio aviso
quebrou.

Sem SMTP_USER/SMTP_PASS no ambiente, imprime e sai com exito: falta de aviso nunca
pode derrubar um passo que funcionou.
"""
import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DESTINO = "paulo@galiciaeducacao.edu.br"
CORES = {"ok": ("#1f6f3f", "FUNCIONOU"),
         "falhou": ("#BA3520", "FALHOU"),
         "pulou": ("#6b6357", "NAO SE APLICA")}

PASSOS = {
    "roteiro": ("1 de 4", "Escrita do roteiro", "15h30"),
    "regua": ("2 de 4", "Regua do roteiro", "17h00"),
    "audio": ("3 de 4", "Gravacao e QA do audio", "18h00"),
    "feed": ("4 de 4", "Publicacao no feed", "05h00"),
}


def main():
    passo = sys.argv[1]
    estado = sys.argv[2] if len(sys.argv) > 2 else "ok"
    detalhe = sys.argv[3] if len(sys.argv) > 3 else ""

    ordem, titulo, hora = PASSOS.get(passo, ("", passo, ""))
    cor, rotulo = CORES.get(estado, CORES["ok"])
    agora = datetime.now(timezone(timedelta(hours=-3)))

    usuario, senha = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS")
    if not usuario or not senha:
        print(f"[{rotulo}] {titulo}: {detalhe} (sem SMTP configurado, nao enviei e-mail)")
        return 0

    html = f"""
    <div style="background:#F4F1EA;padding:32px 24px;font-family:Georgia,'Times New Roman',serif;">
      <div style="max-width:520px;margin:0 auto;background:#ffffff;border:1px solid #ddd6c9;padding:28px;">
        <p style="font-family:Arial,Helvetica,sans-serif;font-size:11px;letter-spacing:2px;
                  text-transform:uppercase;color:#6b6357;margin:0 0 6px;">
          COMPASSO CAPITAL &middot; passo {ordem} &middot; previsto para as {hora}</p>
        <p style="font-family:Arial,Helvetica,sans-serif;font-size:22px;font-weight:bold;
                  color:{cor};margin:0 0 14px;">{rotulo}</p>
        <h1 style="font-weight:normal;font-size:26px;color:#0F1416;margin:0 0 16px;">{titulo}</h1>
        <p style="font-size:16px;line-height:1.6;color:#0F1416;margin:0 0 20px;">{detalhe}</p>
        <p style="font-size:13px;color:#6b6357;border-top:1px solid #e5e0d5;padding-top:14px;margin:0;">
          {agora.strftime('%d/%m/%Y as %H:%M')} de Brasilia<br>
          Voce recebe um aviso por passo, tenha dado certo ou nao. Se um horario passar
          sem e-mail, o proprio aviso falhou: e sinal para olhar o repositorio.</p>
      </div>
    </div>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[{rotulo}] COMPASSO CAPITAL {ordem}: {titulo}"
    msg["From"] = f"COMPASSO CAPITAL <{usuario}>"
    msg["To"] = DESTINO
    msg.attach(MIMEText(f"{rotulo} - {titulo}\n\n{detalhe}", "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        s = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
        s.login(usuario, senha)
        s.sendmail(usuario, [DESTINO], msg.as_string())
        s.quit()
        print(f"aviso enviado: [{rotulo}] {titulo}")
    except Exception as e:
        # aviso que falha nao pode derrubar passo que funcionou
        print(f"::warning::nao consegui enviar o aviso ({e.__class__.__name__}): {detalhe}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
