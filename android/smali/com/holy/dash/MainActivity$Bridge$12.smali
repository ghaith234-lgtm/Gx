.class Lcom/holy/dash/MainActivity$Bridge$12;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge;->setBg(Ljava/lang/String;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$Bridge;

.field final synthetic val$css:Ljava/lang/String;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Bridge;Ljava/lang/String;)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 1236
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$12;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iput-object p2, p0, Lcom/holy/dash/MainActivity$Bridge$12;->val$css:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 3

    .prologue
    .line 1236
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$12;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Bridge$12;->val$css:Ljava/lang/String;

    invoke-static {v1}, Lcom/holy/dash/MainActivity;->parseCssColor(Ljava/lang/String;)I

    move-result v1

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->applyBg(I)V

    return-void
.end method
