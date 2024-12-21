# Maintainer: Your Name <your.email@example.com>

pkgname=wut-cli-git
pkgver=1.0.8
pkgrel=1
pkgdesc="CLI that explains the output of your last command"
arch=('any')
url="https://github.com/shobrook/wut"
license=('MIT')
depends=('python' 'python-openai' 'python-anthropic' 'python-rich' 'python-psutil' 'python-ollama')
makedepends=('python-setuptools' 'python-build' 'python-installer' 'python-wheel' 'git')
source=("git+${url}.git")
sha256sums=('SKIP')

pkgver() {
    cd "${srcdir}/wut"
    git describe --long --tags | sed 's/^v//;s/\([^-]*-g\)/r\1/;s/-/./g'
}

build() {
    cd "${srcdir}/wut"
    python -m build --wheel --no-isolation
}

package() {
    cd "${srcdir}/wut"
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
