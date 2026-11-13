.class Lcom/holy/dash/MainActivity$1;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/holy/dash/MainActivity;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;)V
    .registers 2

    .prologue
    .line 106
    iput-object p1, p0, Lcom/holy/dash/MainActivity$1;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 2

    .prologue
    .line 107
    iget-object v0, p0, Lcom/holy/dash/MainActivity$1;->this$0:Lcom/holy/dash/MainActivity;

    iget-boolean v0, v0, Lcom/holy/dash/MainActivity;->errShown:Z

    if-eqz v0, :cond_13

    iget-object v0, p0, Lcom/holy/dash/MainActivity$1;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-eqz v0, :cond_13

    iget-object v0, p0, Lcom/holy/dash/MainActivity$1;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    invoke-virtual {v0}, Landroid/webkit/WebView;->reload()V

    :cond_13
    return-void
.end method
