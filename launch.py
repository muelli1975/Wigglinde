from wigglinde.app import main
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='--self-test':
        try:main()
        except Exception:
            from pathlib import Path
            import traceback
            Path(sys.argv[2]).write_text(traceback.format_exc(),encoding='utf-8')
            raise SystemExit(1)
    else:main()
