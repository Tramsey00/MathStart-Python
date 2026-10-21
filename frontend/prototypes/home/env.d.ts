declare module 'virtual:mathstart-catalogue' {
  interface Item { title: string; slug: string; order: number; description?: string }
  interface Subject extends Item { grade: string }
  interface Section extends Subject { subject: string }
  interface Topic extends Section { section: string }
  const catalogue: { grades: Item[]; subjects: Subject[]; sections: Section[]; topics: Topic[] };
  export default catalogue;
}
