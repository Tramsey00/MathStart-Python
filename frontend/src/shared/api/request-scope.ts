// I04 must invalidate on logout (including unknown outcome), account switch,
// natural expiry, route disposal and cutover. This is not receipt authority.
export class RequestScope {
  #generation=0;
  #controller:AbortController|null=null;
  invalidate() {this.#generation++;this.#controller?.abort();this.#controller=null;}
  begin() {
    this.invalidate();
    const generation=this.#generation, controller=new AbortController();
    this.#controller=controller;
    return {signal:controller.signal,isCurrent:()=>this.#generation===generation&&!controller.signal.aborted};
  }
  dispose(){this.invalidate();}
}
