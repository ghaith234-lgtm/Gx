.class Lcom/holy/dash/MainActivity$Bridge$7;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge;->setLock(Z)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$Bridge;

.field final synthetic val$on:Z


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Bridge;Z)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 1165
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$7;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iput-boolean p2, p0, Lcom/holy/dash/MainActivity$Bridge$7;->val$on:Z

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 4

    .prologue
    .line 1167
    iget-boolean v0, p0, Lcom/holy/dash/MainActivity$Bridge$7;->val$on:Z

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Bridge$7;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v1, v1, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v1}, Lcom/holy/dash/Prefs;->lock(Landroid/content/Context;)Z

    move-result v1

    if-ne v0, v1, :cond_14

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$7;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->refreshPanel()V

    .line 1175
    :goto_13
    return-void

    .line 1168
    :cond_14
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$7;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->canAuth()Z

    move-result v0

    if-nez v0, :cond_34

    .line 1169
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$7;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    const-string v1, "\ud83d\udd10 \u0641\u0639\u0651\u0644 \u0642\u0641\u0644 \u0627\u0644\u0634\u0627\u0634\u0629 \u0628\u0627\u0644\u0645\u0648\u0628\u0627\u064a\u0644 \u0623\u0648\u0644 (\u0628\u0635\u0645\u0629 \u0623\u0648 \u0631\u0645\u0632) \u2014 \u0645\u0646 \u0625\u0639\u062f\u0627\u062f\u0627\u062a \u0627\u0644\u0623\u0645\u0627\u0646"

    const/4 v2, 0x1

    invoke-static {v0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    .line 1170
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$7;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->refreshPanel()V

    goto :goto_13

    .line 1173
    :cond_34
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$7;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-boolean v1, p0, Lcom/holy/dash/MainActivity$Bridge$7;->val$on:Z

    invoke-static {v1}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;

    move-result-object v1

    iput-object v1, v0, Lcom/holy/dash/MainActivity;->pendingLock:Ljava/lang/Boolean;

    .line 1174
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$7;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->askAuth()V

    goto :goto_13
.end method
