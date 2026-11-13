.class Lcom/holy/dash/Bio$1;
.super Ljava/lang/Object;
.source "Bio.java"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/Bio;->ask(Landroid/app/Activity;Ljava/lang/String;Lcom/holy/dash/Bio$Done;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$d:Lcom/holy/dash/Bio$Done;


# direct methods
.method constructor <init>(Lcom/holy/dash/Bio$Done;)V
    .registers 2
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 45
    iput-object p1, p0, Lcom/holy/dash/Bio$1;->val$d:Lcom/holy/dash/Bio$Done;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/content/DialogInterface;I)V
    .registers 4

    .prologue
    .line 46
    iget-object v0, p0, Lcom/holy/dash/Bio$1;->val$d:Lcom/holy/dash/Bio$Done;

    invoke-interface {v0}, Lcom/holy/dash/Bio$Done;->fallback()V

    return-void
.end method
