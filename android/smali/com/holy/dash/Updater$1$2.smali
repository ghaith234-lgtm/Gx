.class Lcom/holy/dash/Updater$1$2;
.super Ljava/lang/Object;
.source "Updater.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/Updater$1;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/Updater$1;


# direct methods
.method constructor <init>(Lcom/holy/dash/Updater$1;)V
    .registers 2

    .prologue
    .line 70
    iput-object p1, p0, Lcom/holy/dash/Updater$1$2;->this$0:Lcom/holy/dash/Updater$1;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 4

    .prologue
    .line 71
    iget-object v0, p0, Lcom/holy/dash/Updater$1$2;->this$0:Lcom/holy/dash/Updater$1;

    iget-object v0, v0, Lcom/holy/dash/Updater$1;->val$a:Landroid/app/Activity;

    const-string v1, "\u062a\u0639\u0630\u0651\u0631 \u0641\u062d\u0635 \u0627\u0644\u062a\u062d\u062f\u064a\u062b \u2014 \u0627\u062f\u062e\u0644 \u0627\u0644\u0644\u0648\u062d\u0629 \u0648\u062d\u0627\u0648\u0644"

    const/4 v2, 0x1

    invoke-static {v0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    return-void
.end method
