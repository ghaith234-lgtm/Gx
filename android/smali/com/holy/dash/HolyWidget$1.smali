.class Lcom/holy/dash/HolyWidget$1;
.super Ljava/lang/Object;
.source "HolyWidget.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/HolyWidget;->refreshAsync(Landroid/content/Context;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$a:Landroid/content/Context;


# direct methods
.method constructor <init>(Landroid/content/Context;)V
    .registers 2
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 101
    iput-object p1, p0, Lcom/holy/dash/HolyWidget$1;->val$a:Landroid/content/Context;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 2

    .prologue
    .line 104
    iget-object v0, p0, Lcom/holy/dash/HolyWidget$1;->val$a:Landroid/content/Context;

    invoke-static {v0}, Lcom/holy/dash/HolyWidget;->fetch(Landroid/content/Context;)V

    .line 105
    return-void
.end method
