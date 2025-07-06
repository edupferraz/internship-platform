const Footer = () => {
  return (
    <footer className="bg-[--card] text-[--card-foreground] p-6 md:p-8 rounded-t-lg mt-12 border-t border-[--border]">
      <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-6 md:gap-8">
        <div className="flex flex-col items-center md:items-start text-center md:text-left">
          <p className="font-semibold text-lg text-[--foreground]">internship.platform</p>
          <p className="text-sm text-[--muted-foreground] mt-1">
            &copy; {new Date().getFullYear()} Todos os direitos reservados.
          </p>
        </div>

        <nav className="flex flex-wrap justify-center md:justify-end gap-x-6 gap-y-3 text-base">
          <a
            href="/termos"
            className="text-[--muted-foreground] hover:text-[--primary] transition-colors duration-200 ease-in-out"
          >
            Termos de Uso
          </a>
          <a
            href="/privacidade"
            className="text-[--muted-foreground] hover:text-[--primary] transition-colors duration-200 ease-in-out"
          >
            Política de Privacidade
          </a>
          <a
            href="/contato"
            className="text-[--muted-foreground] hover:text-[--primary] transition-colors duration-200 ease-in-out"
          >
            Contato
          </a>
        </nav>
      </div>
    </footer>
  );
};

export default Footer;