.class Lcom/holy/dash/MainActivity$7$1;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$7;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$7;

.field final synthetic val$fine:Z


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$7;Z)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 369
    iput-object p1, p0, Lcom/holy/dash/MainActivity$7$1;->this$1:Lcom/holy/dash/MainActivity$7;

    iput-boolean p2, p0, Lcom/holy/dash/MainActivity$7$1;->val$fine:Z

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 3

    .prologue
    .line 371
    iget-boolean v0, p0, Lcom/holy/dash/MainActivity$7$1;->val$fine:Z

    if-eqz v0, :cond_10

    iget-object v0, p0, Lcom/holy/dash/MainActivity$7$1;->this$1:Lcom/holy/dash/MainActivity$7;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$7;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$7$1;->this$1:Lcom/holy/dash/MainActivity$7;

    iget-object v1, v1, Lcom/holy/dash/MainActivity$7;->val$o:Ljava/lang/String;

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->useOrigin(Ljava/lang/String;)V

    .line 375
    :goto_f
    return-void

    .line 372
    :cond_10
    iget-object v0, p0, Lcom/holy/dash/MainActivity$7$1;->this$1:Lcom/holy/dash/MainActivity$7;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$7;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->setupMsg:Landroid/widget/TextView;

    const v1, -0x48e7b

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setTextColor(I)V

    .line 373
    iget-object v0, p0, Lcom/holy/dash/MainActivity$7$1;->this$1:Lcom/holy/dash/MainActivity$7;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$7;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->setupMsg:Landroid/widget/TextView;

    const-string v1, "\u0645\u0627 \u0648\u0635\u0644\u062a \u0644\u0644\u0648\u062d\u0629 \u0639\u0644\u0649 \u0647\u0630\u0627 \u0627\u0644\u0639\u0646\u0648\u0627\u0646 \u2014 \u062a\u0623\u0643\u062f \u0625\u0646\u0647\u0627 \u0634\u063a\u0651\u0627\u0644\u0629 \u0648\u0627\u0644\u0645\u0648\u0628\u0627\u064a\u0644 \u0645\u062a\u0635\u0644 \u0628\u0627\u0644\u0625\u0646\u062a\u0631\u0646\u062a.\n\u0627\u0636\u063a\u0637 \u0645\u0637\u0648\u0651\u0644\u0627\u064b \u0639\u0644\u0649 \u00ab\u0627\u062a\u0635\u0627\u0644\u00bb \u062d\u062a\u0649 \u062a\u062d\u0641\u0638\u0647 \u0628\u0643\u0644 \u0627\u0644\u0623\u062d\u0648\u0627\u0644."

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 374
    iget-object v0, p0, Lcom/holy/dash/MainActivity$7$1;->this$1:Lcom/holy/dash/MainActivity$7;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$7;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$7$1;->this$1:Lcom/holy/dash/MainActivity$7;

    iget-object v1, v1, Lcom/holy/dash/MainActivity$7;->val$o:Ljava/lang/String;

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->setupLongPress(Ljava/lang/String;)V

    goto :goto_f
.end method
