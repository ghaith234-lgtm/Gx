.class Lcom/holy/dash/MainActivity$Bridge$9$1;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge$9;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$2:Lcom/holy/dash/MainActivity$Bridge$9;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Bridge$9;)V
    .registers 2

    .prologue
    .line 1210
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$9$1;->this$2:Lcom/holy/dash/MainActivity$Bridge$9;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 2

    .prologue
    .line 1210
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$9$1;->this$2:Lcom/holy/dash/MainActivity$Bridge$9;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge$9;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->refreshPanel()V

    return-void
.end method
