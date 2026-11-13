.class final Lcom/holy/dash/Net$Resp;
.super Ljava/lang/Object;
.source "Net.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/holy/dash/Net;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x18
    name = "Resp"
.end annotation


# instance fields
.field final body:Ljava/lang/String;

.field final code:I


# direct methods
.method constructor <init>(ILjava/lang/String;)V
    .registers 3

    .prologue
    .line 24
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput p1, p0, Lcom/holy/dash/Net$Resp;->code:I

    iput-object p2, p0, Lcom/holy/dash/Net$Resp;->body:Ljava/lang/String;

    return-void
.end method
